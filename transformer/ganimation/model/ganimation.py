import torch
from .base_model import BaseModel
from . import model_utils


class GANimationModel(BaseModel):
    """继承，重写BaseModel"""
    def __init__(self):
        super(GANimationModel, self).__init__()
        #父类初始化
        self.name = "GANimation"
        #重写name

    def initialize(self, opt):
        super(GANimationModel, self).initialize(opt)
        #父类初始化

        self.net_gen = model_utils.define_splitG(self.opt.img_nc,#通道数
                                                 self.opt.aus_nc, #AU向量维数
                                                 self.opt.ngf, #net_gen基础feature map数目
                                                 use_dropout=self.opt.use_dropout,#switch for dropoout 
                                                 norm=self.opt.norm, #normalization方式
                                                 init_type=self.opt.init_type, #网络参数初始化策略
                                                 init_gain=self.opt.init_gain, #初始化的scaling factor
                                                 gpu_ids=self.gpu_ids)
        self.models_name.append('gen')
        #维护model记录
        
        if self.is_train:
        	#测试时不辩别，如果要评估就用训练模式吧，或者改改结构
            self.net_dis = model_utils.define_splitD(self.opt.img_nc, 
                                                     self.opt.aus_nc, 
                                                     self.opt.final_size, #预处理后图片的大小
                                                     self.opt.ndf, 
                                                     norm=self.opt.norm, 
                                                     init_type=self.opt.init_type, 
                                                     init_gain=self.opt.init_gain, 
                                                     gpu_ids=self.gpu_ids)
            self.models_name.append('dis')
            #维护model记录

        if self.opt.load_epoch > 0:
            self.load_ckpt(self.opt.load_epoch)
            #载入epoch


    def setup(self):
        super(GANimationModel, self).setup()
        #父类调用
        if self.is_train:
            # setup optimizer
            self.optim_gen = torch.optim.Adam(self.net_gen.parameters(),
                                              lr=self.opt.lr,  
                                              betas=(self.opt.beta1, 0.999))
            self.optims.append(self.optim_gen)

            self.optim_dis = torch.optim.Adam(self.net_dis.parameters(), 
                                              lr=self.opt.lr, 
                                              betas=(self.opt.beta1, 0.999))
            self.optims.append(self.optim_dis)

            # setup schedulers
            #每一个optimizer一个scheduler
            self.schedulers = [model_utils.get_scheduler(optim, self.opt) for optim in self.optims]

    def feed_batch(self, batch):
    	#就是转移预处理
        self.src_img = batch['src_img'].to(self.device)
        self.tar_aus = batch['tar_aus'].type(torch.FloatTensor).to(self.device)
        if self.is_train:
            self.src_aus = batch['src_aus'].type(torch.FloatTensor).to(self.device)
            self.tar_img = batch['tar_img'].to(self.device)

    def forward(self):
        # generate fake image

        #aus_mask是注意力掩膜
        #？？？embed
        self.color_mask ,self.aus_mask, self.embed = self.net_gen(self.src_img, self.tar_aus)
        self.fake_img = self.aus_mask * self.src_img + (1 - self.aus_mask) * self.color_mask

        # reconstruct real image
        if self.is_train:
            self.rec_color_mask, self.rec_aus_mask, self.rec_embed = self.net_gen(self.fake_img, self.src_aus)
            self.rec_real_img = self.rec_aus_mask * self.fake_img + (1 - self.rec_aus_mask) * self.rec_color_mask

    def backward_dis(self):
        # real image
        pred_real, self.pred_real_aus = self.net_dis(self.src_img)
        self.loss_dis_real = self.criterionGAN(pred_real, True)
        self.loss_dis_real_aus = self.criterionMSE(self.pred_real_aus, self.src_aus)

        # fake image, detach to stop backward to generator
        pred_fake, _ = self.net_dis(self.fake_img.detach()) 
        self.loss_dis_fake = self.criterionGAN(pred_fake, False)

        # combine dis loss
        #lambda means weight here
        self.loss_dis =   self.opt.lambda_dis * (self.loss_dis_fake + self.loss_dis_real) \
                        + self.opt.lambda_aus * self.loss_dis_real_aus
   
        if self.opt.gan_type == 'wgan-gp':
            self.loss_dis_gp = self.gradient_penalty(self.src_img, self.fake_img)
            self.loss_dis = self.loss_dis + self.opt.lambda_wgan_gp * self.loss_dis_gp
        
        # backward discriminator loss
        self.loss_dis.backward()

    def backward_gen(self):	
        # original to target domain, should fake the discriminator
        pred_fake, self.pred_fake_aus = self.net_dis(self.fake_img)
        self.loss_gen_GAN = self.criterionGAN(pred_fake, True)
        #pred值是图片为真的概率，True or False表示计算相对于True或者False的损失
        self.loss_gen_fake_aus = self.criterionMSE(self.pred_fake_aus, self.tar_aus)

        # target to original domain reconstruct, identity loss
        self.loss_gen_rec = self.criterionL1(self.rec_real_img, self.src_img)
        #L1重建损失

        # constrain on AUs mask（注意的是动作，所以也叫aus_mask）
        #real_img ,fake_img 都会有一张注意力掩膜
        self.loss_gen_mask_real_aus = torch.mean(self.aus_mask)
        self.loss_gen_mask_fake_aus = torch.mean(self.rec_aus_mask)
        #你不能全部都注意吧，这是防止每个地方注意力都为1这种牛皮的情况

        self.loss_gen_smooth_real_aus = self.criterionTV(self.aus_mask)
        self.loss_gen_smooth_fake_aus = self.criterionTV(self.rec_aus_mask)
        #你的注意力不能过于集中吧，这个平滑处理



        # combine and backward G loss
        self.loss_gen =   self.opt.lambda_dis * self.loss_gen_GAN \
                        + self.opt.lambda_aus * self.loss_gen_fake_aus \
                        + self.opt.lambda_rec * self.loss_gen_rec \
                        + self.opt.lambda_mask * (self.loss_gen_mask_real_aus + self.loss_gen_mask_fake_aus) \
                        + self.opt.lambda_tv * (self.loss_gen_smooth_real_aus + self.loss_gen_smooth_fake_aus)

        self.loss_gen.backward()

    def optimize_paras(self, train_gen):
        self.forward()
        # update discriminator
        self.set_requires_grad(self.net_dis, True)
        self.optim_dis.zero_grad()#clear
        self.backward_dis()#backward时开始计算grad
        self.optim_dis.step()

        # update G if needed
        if train_gen:
            self.set_requires_grad(self.net_dis, False)
            self.optim_gen.zero_grad()
            self.backward_gen()
            self.optim_gen.step()

    def save_ckpt(self, epoch):
        # save the specific networks
        save_models_name = ['gen', 'dis']
        return super(GANimationModel, self).save_ckpt(epoch, save_models_name)

    def load_ckpt(self, epoch):
        # load the specific part of networks
        load_models_name = ['gen']
        if self.is_train:
            load_models_name.extend(['dis'])
        return super(GANimationModel, self).load_ckpt(epoch, load_models_name)

    def clean_ckpt(self, epoch):
        # delete the specific part of networks' checkpoints
        load_models_name = ['gen', 'dis']
        return super(GANimationModel, self).clean_ckpt(epoch, load_models_name)

    def get_latest_losses(self):
    	#设置显示的损失
        get_losses_name = ['dis_fake', 'dis_real', 'dis_real_aus', 'gen_rec']
        return super(GANimationModel, self).get_latest_losses(get_losses_name)

    def get_latest_visuals(self):
    	#设置可视化的部分
        visuals_name = ['src_img', 'tar_img', 'color_mask', 'aus_mask', 'fake_img']
        if self.is_train:
            visuals_name.extend(['rec_color_mask', 'rec_aus_mask', 'rec_real_img'])
        return super(GANimationModel, self).get_latest_visuals(visuals_name)
