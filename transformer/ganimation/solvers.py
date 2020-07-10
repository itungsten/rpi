from .data import create_dataloader
from .model import create_model
from .visualizer import Visualizer
import copy
import time
import os
import torch
import numpy as np
from PIL import Image
import pickle
from torchvision import transforms


def create_solver(opt):
    #返回一个用配置文件初始化的求解器
    return Solver(opt)




class Solver(object):
    def __init__(self,opt):
        super(Solver, self).__init__()
        #调用父类初始化
        self.initialize(opt)
        #自己初始化

    def initialize(self, opt):
        self.opt = opt
        #保存配置
        self.visual = Visualizer(opt)
        #用配置创建一个visdom对象作为附件

    def run_solver(self):
        if self.opt.mode == "train":
            self.train_networks()
            #训练
        else:
            self.test_networks(self.opt)
            #测试

    def train_networks(self):
        # init train setting
        self.init_train_setting()

        #epoch_count是开始值，epoch_len最终
        for epoch in range(self.opt.epoch_count, self.epoch_len + 1):
            self.train_epoch(epoch)
            #以epoch为单元的训练

            self.cur_lr = self.train_model.update_learning_rate()
            #学习率是按epoch变化的，就像复习一样，看太多了，学习的新知识就相对少了


            #按频率保存checkpoints
            if epoch % self.opt.save_epoch_freq == 0:
                self.train_model.save_ckpt(epoch)

        #总要保存最后一个
        self.train_model.save_ckpt(self.epoch_len)

    def init_train_setting(self):
        self.train_dataset = create_dataloader(self.opt)
        #传入配置创建数据集（按数组的思维看来就是loader）
        self.train_model = create_model(self.opt)
        #传入配置创建模型

        self.train_total_steps = 0
        #训练了的次数

        self.epoch_len = self.opt.niter + self.opt.niter_decay
        #总epoch是学习率不变的和学习率线性衰减部分之和
        
        self.cur_lr = self.opt.lr
        #当前学习率

    def train_epoch(self, epoch):
        epoch_start_time = time.time()
        #开始时间
        epoch_steps = 0
        #当前epoch的step数，img==step->batch->epoch==iteration

        last_print_step_t = time.time()
        #初始化上次控制台呈现的时间为开始时间

        for idx, batch in enumerate(self.train_dataset):

            self.train_total_steps += self.opt.batch_size
            #step->batch

            epoch_steps += self.opt.batch_size

            
            self.train_model.feed_batch(batch)
            #forward

            self.train_model.optimize_paras(train_gen=(idx % self.opt.train_gen_iter == 0))
            #backward
            #每隔self.opt.train_gen_iter个batch，训练一次生成器

            #输出损失
            if self.train_total_steps % self.opt.print_losses_freq == 0:
                cur_losses = self.train_model.get_latest_losses()
                #获得当前损失（多种损失组成的字典）

                avg_step_t = (time.time() - last_print_step_t) / self.opt.print_losses_freq
                #每张图片处理时间

                last_print_step_t = time.time()
                #更新

                #命令行输出损失
                info_dict = {'epoch': epoch, 
                             'epoch_len': self.epoch_len,
                             'epoch_steps': epoch_steps,
                             'epoch_steps_len': len(self.train_dataset),
                             'step_time': avg_step_t,
                             'cur_lr': self.cur_lr,
                             'log_path': os.path.join(self.opt.ckpt_dir, self.opt.log_file),
                             'losses': cur_losses
                            }
                self.visual.print_losses_info(info_dict)
            
            #visdom绘制loss map
            if self.train_total_steps % self.opt.plot_losses_freq == 0 and self.visual.display_id > 0:
                #按频率展示，id表示是否启用

                cur_losses = self.train_model.get_latest_losses()
                self.visual.display_current_losses(epoch - 1, epoch_steps / len(self.train_dataset), cur_losses)
                #？？？len这个魔法函数可能返回总图片数吧
                #？？？epoch-1
            
            #visdom展示图片
            if self.train_total_steps % self.opt.sample_img_freq == 0 and self.visual.display_id > 0:
                #按频率展示，id表示是否启用

                cur_vis = self.train_model.get_latest_visuals()
                self.visual.display_online_results(cur_vis, epoch)

                #打印AU向量的伪代码
                # latest_aus = self.train_model.get_latest_aus()
                # visual.log_aus(epoch, epoch_steps, latest_aus, opt.ckpt_dir)

    def single_networks(self,opt):
        self.init_single_setting(opt)
        self.single_ops()

    def init_single_setting(self,opt):
        self.single_data=opt.data_root
        self.single_model=create_model(opt)
    def single_ops(self):
        transform_list = []
        if self.opt.resize_or_crop == 'resize_and_crop':
            transform_list.append(transforms.Resize([self.opt.load_size, self.opt.load_size], Image.BICUBIC))
            transform_list.append(transforms.RandomCrop(self.opt.final_size))
        elif self.opt.resize_or_crop == 'crop':
            transform_list.append(transforms.RandomCrop(self.opt.final_size))
        elif self.opt.resize_or_crop == 'none':
            pass
            # transform_list.append(transforms.Lambda(lambda image: image))
            #其实就是返回原图，可以用注释掉，用pass占位，windows下就不会出错了
        else:
            raise ValueError("--resize_or_crop %s is not a valid option." % self.opt.resize_or_crop)
            #不是枚举值

        if self.is_train and (not self.opt.no_flip):
            transform_list.append(transforms.RandomHorizontalFlip())
            #上下翻转

        transform_list.append(transforms.ToTensor())
        #转化为Tensor
        transform_list.append(transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)))
        #正则化

        img2tensor = transforms.Compose(transform_list)
        #打包哦
        single_img=Image.open(self.opt.data_root).convert('RGB')
        single_img=img2tensor(single_img)
        single_img=single_img.unsqueeze(0)
        # print("hello peko")
        # print(single_img.shape)
        # return;
        with torch.no_grad():

            faces_list = list(single_img.float().numpy())
            #转化为float是方便计算，转换numpy是因为本来是tensor，注意是list的list

            #path源，目标成对出现，注意是list的list

            # interpolate several times（插值 平滑）
            tar_aus=self.opt.tarAus
            tar_aus=[i/5 for i in tar_aus]
            tar_aus=[tar_aus,]

            with open(self.opt.ausPath,'rb') as f:
                src_aus=pickle.load(f)
            # src_aus=[0.00, 0.00, 0.00, 0.32, 0.03, 1.49, 0.47, 0.00, 0.35, 0.18, 0.00, 0.00, 0.00, 0.00, 0.04, 0.20, 0.00]
            #58
            # print(src_aus)
            src_aus=[i/5 for i in src_aus]
            src_aus=[src_aus,]
            
            tar_aus=torch.Tensor(tar_aus)
            src_aus=torch.Tensor(src_aus)
            # print(single_img.shape)
            # print(tar_aus.shape)
            # print(src_aus.shape)
            # src_aus=[[0.55, 0.00, 0.00, 0.45, 0.46, 0.00, 0.26, 0.55, 1.31, 1.01, 0.00, 0.00, 1.18, 0.00, 0.0, 0.0, 0.0],]
            for idx in range(self.opt.interpolate_len):
                cur_alpha = (idx + 1.0) / float(self.opt.interpolate_len)
                #alpah是AU的激活度

                cur_tar_aus = cur_alpha * tar_aus  + (1 - cur_alpha) * src_aus 
                #AUs按激活度加权,注意有src，tar，gen。其中gen=src+tar

                test_batch = {'src_img': single_img, 'tar_aus': cur_tar_aus, 'src_aus':src_aus, 'tar_img':torch.Tensor([])}
                #基于alpha新构造的batch

                self.single_model.feed_batch(test_batch)
                self.single_model.forward()
                #前向传播

                cur_gen_faces = self.single_model.fake_img.squeeze(0).cpu().float().numpy()
                #fake_img在gpu计算完成后，搬运到cpu上，再float，再numpy

                faces_list.append(cur_gen_faces)
                # print(len(faces_list))
                #list of numpy
                #cur_gen_faces是当前激活度下的fake_img


            for (face_idx,face) in enumerate(faces_list):
                img = np.array(self.visual.numpy2im(faces_list[face_idx]))
                img = Image.fromarray(img)
            # save image
                saved_path = os.path.join(self.opt.results, "%d.png" % (face_idx+1))
                img.save(saved_path)




    def test_networks(self, opt):
        self.init_test_setting(opt)
        self.test_ops()

    def init_test_setting(self, opt):
        self.test_dataset = create_dataloader(opt)
        #构造测试数据集
        self.test_model = create_model(opt)
        #构造测试模型

    def test_ops(self):
        for batch_idx, batch in enumerate(self.test_dataset):

            #避免重名用batch_idx

            print(batch['src_img'].shape)
            print(batch['tar_aus'])
            print(batch['src_aus'])
            #测试时不计算梯度
            with torch.no_grad():
                #batch层次
                
                
                faces_list = [batch['src_img'].float().numpy()]
                #转化为float是方便计算，转换numpy是因为本来是tensor，注意是list的list

                paths_list = [batch['src_path'], batch['tar_path']]
                #path源，目标成对出现，注意是list的list

                # interpolate several times（插值 平滑）
                for idx in range(self.opt.interpolate_len):
                    cur_alpha = (idx + 1.0) / float(self.opt.interpolate_len)
                    #alpah是AU的激活度

                    
                    cur_tar_aus = cur_alpha * batch['tar_aus'] + (1 - cur_alpha) * batch['src_aus']
                    #AUs按激活度加权,注意有src，tar，gen。其中gen=src+tar

                    test_batch = {'src_img': batch['src_img'], 'tar_aus': cur_tar_aus, 'src_aus':batch['src_aus'], 'tar_img':batch['tar_img']}
                    #基于alpha新构造的batch

                    self.test_model.feed_batch(test_batch)
                    self.test_model.forward()
                    #前向传播

                    cur_gen_faces = self.test_model.fake_img.cpu().float().numpy()
                    #fake_img在gpu计算完成后，搬运到cpu上，再float，再numpy

                    faces_list.append(cur_gen_faces)
                    #cur_gen_faces是当前激活度下的fake_img

                faces_list.append(batch['tar_img'].float().numpy())

                #faces_list==[[src],[fake1],[fake2],...,[fake(len)],[tar]]

            self.test_save_imgs(faces_list, paths_list)
            #每个batch保存哒

    def test_save_imgs(self, faces_list, paths_list):
        for idx in range(len(paths_list[0])):
            #batch_size

            src_name = os.path.splitext(os.path.basename(paths_list[0][idx]))[0]
            tar_name = os.path.splitext(os.path.basename(paths_list[1][idx]))[0]
            #这里basename包括扩展名，splitext按扩展名切分

            if self.opt.save_test_gif:
                #输出动图
                import imageio
                #动图的库。。。大多数都是numpy接口嘛
                
                imgs_numpy_list = []

                for face_idx in range(len(faces_list) - 1):  
                    #-1 means to remove target image
                    #list的len都是直接元素的数目

                    cur_numpy = np.array(self.visual.numpy2im(faces_list[face_idx][idx]))
                    #转化为numpy

                    imgs_numpy_list.extend([cur_numpy for _ in range(3)])
                    #复制三份，为了延时


                saved_path = os.path.join(self.opt.results, "%s_%s.gif" % (src_name, tar_name))
                #opt.results/src_tar.gif

                imageio.mimsave(saved_path, imgs_numpy_list)
            else:
                # #和应用无关，懒得写


                # concate src, inters, tar faces
                concate_img = np.array(self.visual.numpy2im(faces_list[0][idx]))
                for face_idx in range(1, len(faces_list)):
                    concate_img = np.concatenate((concate_img, np.array(self.visual.numpy2im(faces_list[face_idx][idx]))), axis=1)
                concate_img = Image.fromarray(concate_img)
                # save image
                saved_path = os.path.join(self.opt.results, "%s_%s.jpg" % (src_name, tar_name))
                concate_img.save(saved_path)


                            #和应用无关，懒得写


                # concate src, inters, tar faces
                # for (face_idx,face) in enumerate(faces_list):
                #     if((face_idx+1)==len(faces_list)):
                #         break
                #     img = np.array(self.visual.numpy2im(faces_list[face_idx][idx]))
                #     img = Image.fromarray(img)
                # # save image
                #     saved_path = os.path.join(self.opt.results, "%d.png" % (face_idx+1))
                #     img.save(saved_path)

            # print("[Success] Saved images to %s" % saved_path)
