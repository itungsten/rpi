import torch
import os
from collections import OrderedDict
import random
from . import model_utils

class BaseModel:
    """py3默认继承object"""
    def __init__(self):
        super(BaseModel, self).__init__()
        self.name = "Base"
        #子类重写模型名称

    def initialize(self, opt):
        self.opt = opt
        self.gpu_ids = self.opt.gpu_ids
        #不是很赞成这种写法，应该统一在self.opt里面
        self.device = torch.device('cuda:%d' % self.gpu_ids[0] if self.gpu_ids else 'cpu')
        #反正不是cuda:0 就是cpu
        self.is_train = (self.opt.mode == "train")
        # inherit to define network model 
        self.models_name = []
        #子类中用于存放模型名

    def setup(self):
        # print("%s with Model [%s]" % (self.opt.mode.capitalize(), self.name))
        #命令行输出的开始提示信息

        if self.is_train:
        	#训练
            self.set_train()

            #定义损失函数，在device上计算
            self.criterionGAN = model_utils.GANLoss(gan_type=self.opt.gan_type).to(self.device)
            self.criterionL1 = torch.nn.L1Loss().to(self.device)
            self.criterionMSE = torch.nn.MSELoss().to(self.device)
            self.criterionTV = model_utils.TVLoss().to(self.device)

            #？？？并行计算？？？gpu_ids是一个列表
            torch.nn.DataParallel(self.criterionGAN, self.gpu_ids)
            torch.nn.DataParallel(self.criterionL1, self.gpu_ids)
            torch.nn.DataParallel(self.criterionMSE, self.gpu_ids)
            torch.nn.DataParallel(self.criterionTV, self.gpu_ids)

            # inherit to set up train/val/test status
            #？？？？？？
            self.losses_name = []
            self.optims = []
            #优化器对象列表
            self.schedulers = []
        else:
        	#Set model to Test state
            self.set_test()

    def set_test(self):
        # print("Set model to Test state.")
        for name in self.models_name:
            if isinstance(name, str):
                net = getattr(self, 'net_' + name)
                #获得网络层
                if (not self.opt.no_test_eval):
                	#就是测试的时候使用评估模型（评估模型最主要是BN使用全样本，Dropout失效）
                    net.eval()
                    # print("Set net_%s to EVAL." % name)
                else:
                	#否则使用训练模型
                    net.train()
        self.is_train = False

    def set_train(self):
        # print("Set model to Train state.")
        for name in self.models_name:
            if isinstance(name, str):
                net = getattr(self, 'net_' + name)
                net.train()
                #把每个网路层设置到训练状态
                # print("Set net_%s to TRAIN." % name)
        self.is_train = True

    def set_requires_grad(self, parameters, requires_grad=False):
    	#注意这里默认是False
        if not isinstance(parameters, list):
            parameters = [parameters]
            #包装一下（对单参数）
        for param in parameters:
            if param is not None:
                param.requires_grad = requires_grad

    def get_latest_visuals(self, visuals_name):
    	#visuals_name is a list of name to visualize
        visual_ret = OrderedDict()
        #学过汇编的都知道，ret is return
        for name in visuals_name:
            if isinstance(name, str) and hasattr(self, name):
                visual_ret[name] = getattr(self, name)
                #[]就和c++STL的map一样，自动创建
        return visual_ret

    def get_latest_losses(self, losses_name):
        errors_ret = OrderedDict()
        for name in losses_name:
            if isinstance(name, str):
                cur_loss = float(getattr(self, 'loss_' + name))
                #introspect赛高！
                errors_ret[name] = cur_loss
                #[]就和c++STL的map一样，自动创建
        return errors_ret

    def feed_batch(self, batch):
    	#重写
        pass 

    def forward(self):
    	#重写
        pass

    def optimize_paras(self):
    	#重写
        pass

    def update_learning_rate(self):
    	#scheduler在model_utils里面
        for scheduler in self.schedulers:
            scheduler.step()
        lr = self.optims[0].param_groups[0]['lr']
        return lr

    def save_ckpt(self, epoch, models_name):
        for name in models_name:
            if isinstance(name, str):
                save_filename = '%s_net_%s.pth' % (epoch, name)
                #格式化文件名
                save_path = os.path.join(self.opt.ckpt_dir, save_filename)
                #保存路径
                net = getattr(self, 'net_' + name)
                #introspect

                # save cpu params, so that it can be used in other GPU settings
                if len(self.gpu_ids) > 0 and torch.cuda.is_available():
                    torch.save(net.module.cpu().state_dict(), save_path)
                	#使用了gpu的情况下，保存checkpoints先转移到cpu，提高通用性
                    net.to(self.gpu_ids[0])
                    #搬回去
                    net = torch.nn.DataParallel(net, self.gpu_ids)
                    #并行处理，生成并行化的模型
                else:
                    torch.save(net.cpu().state_dict(), save_path)

    def load_ckpt(self, epoch, models_name):
        #每个网络层都加载一次
        for name in models_name:
            if isinstance(name, str):
                load_filename = '%s_net_%s.pth' % (epoch, name)
                load_path = os.path.join(self.opt.ckpt_dir, load_filename)
                #pth路径
                assert os.path.isfile(load_path), "File '%s' does not exist." % load_path
                #断言检验
                
                pretrained_state_dict = torch.load(load_path, map_location=str(self.device))
                #数据在不同设备上处理是不一样的要映射一下

                if hasattr(pretrained_state_dict, '_metadata'):
                    del pretrained_state_dict._metadata

                net = getattr(self, 'net_' + name)
                if isinstance(net, torch.nn.DataParallel):
                    net = net.module

                # load only existing keys
                pretrained_dict = {k: v for k, v in pretrained_state_dict.items() if k in net.state_dict()}
                #for是生成器 if是过滤器 这里过滤无用键值对
                net.load_state_dict(pretrained_dict)
                # print("[Info] Successfully load trained weights for %s_net_%s." % (epoch,name))
                #prompt

    def clean_ckpt(self, epoch, models_name):
    	#删除一个epoch下的models的checkpoints文件
        for name in models_name:
            if isinstance(name, str):
                load_filename = '%s_net_%s.pth' % (epoch, name)
                load_path = os.path.join(self.opt.ckpt_dir, load_filename)
                if os.path.isfile(load_path):
                    os.remove(load_path)

    def gradient_penalty(self, input_img, generate_img):
        #我也不知道为什么要用插值图片计算

        alpha = torch.rand(input_img.size(0), 1, 1, 1).to(self.device)
        #gpu设备默认cuda:0，alpha是随机数
        inter_img = (alpha * input_img.data + (1 - alpha) * generate_img.data).requires_grad_(True)
        inter_img_prob, _ = self.net_dis(inter_img)
        #返回probability和AU向量

        # computer gradient penalty: x: inter_img, y: inter_img_prob
        # (L2_norm(dy/dx) - 1)**2
        dydx = torch.autograd.grad(outputs=inter_img_prob,
                                   inputs=inter_img,
                                   grad_outputs=torch.ones(inter_img_prob.size()).to(self.device),
                                   retain_graph=True,
                                   create_graph=True,
                                   only_inputs=True)[0]
        #求梯度就对了

        dydx = dydx.view(dydx.size(0), -1)
        #拉成一维
        dydx_l2norm = torch.sqrt(torch.sum(dydx ** 2, dim=1))
        #L2范数
        return torch.mean((dydx_l2norm - 1) ** 2) 