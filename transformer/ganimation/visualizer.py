import os
import numpy as np
import torch
import math
from PIL import Image



class Visualizer(object):

    def __init__(self,opt):
        super(Visualizer, self).__init__()
        #调用父类默认初始化
        self.initialize(opt)
        #使用配置初始化

    def initialize(self, opt):
        self.opt = opt
        #copy配置
        self.display_id = self.opt.visdom_display_id
        #id==0时不启用

        if self.display_id > 0:
            import visdom 
            self.vis = visdom.Visdom(server="http://localhost", port=self.opt.visdom_port, env=self.opt.visdom_env)
            #创建vis对象
            self.ncols = 8
            #八张图片一组，一共有八列


    def throw_visdom_connection_error(self):
    	#visdom异常处理
        print('\n\nno visdom server.')
        exit(1)

    def print_losses_info(self, info_dict):
        """命令行和log文件 损失信息"""


        msg = '[{}][Epoch: {:0>3}/{:0>3}; Images: {:0>4}/{:0>4}; Time: {:.3f}s/Batch({}); LR: {:.7f}] '.format(
                self.opt.name, 
                info_dict['epoch'], 
                info_dict['epoch_len'], 
                info_dict['epoch_steps'], 
                info_dict['epoch_steps_len'], 
                info_dict['step_time'], 
                self.opt.batch_size, 
                info_dict['cur_lr'])
        #{}是格式化，:0>3，是用0占位(:)，右对齐(>)，宽度为3


        for k, v in info_dict['losses'].items():
            msg += '| {}: {:.4f} '.format(k, v)
        #losses里面有n多种loss嘛
        msg += '|'

        print(msg)

        with open(info_dict['log_path'], 'a+') as f:
            f.write(msg + '\n')
        #log文件

    def display_current_losses(self, epoch, counter_ratio, losses_dict):
        """visdom 损失信息"""
        
        if not hasattr(self, 'plot_data'):
            self.plot_data = {'X': [], 'Y': [], 'legend': list(losses_dict.keys())}
            #打印数据初始化
            #图注是各种损失的名称

        self.plot_data['X'].append(epoch + counter_ratio)
        #epoch+counter_ratio就是精确到小数的训练epoch数，作为横坐标
        #(n,)
        self.plot_data['Y'].append( [ losses_dict[k] for k in self.plot_data['legend'] ] )
        #(n,m)
        #对每个损失有一条曲线，这里是一个X对应的Y们的列表

        try:
        	#画多条折线
            self.vis.line(
                X=np.stack([np.array(self.plot_data['X'])] * len(self.plot_data['legend']), 1),
                #(n)->(n,m)
                Y=np.array(self.plot_data['Y']),
                opts={
                    'title': self.opt.name + ' loss over time',
                    'legend':self.plot_data['legend'],
                    'xlabel':'epoch',
                    'ylabel':'loss'},
                win=self.display_id)
                #一些显示设置
        except ConnectionError:
        	#连接失败
            self.throw_visdom_connection_error()

    def display_online_results(self, visuals, epoch):
        win_id = self.display_id + 24
        #不懂，反正从24开始

        images = []
        labels = []
        for label, image in visuals.items():
            if 'mask' in label:  # or 'focus' in label:
                image = (image - 0.5) / 0.5   # convert map from [0, 1] to [-1, 1]
            #可能掩膜图就要这个样子吧

            image_numpy = self.tensor2im(image)
            images.append(image_numpy.transpose([2, 0, 1]))
            #通道数最前C x W x H
            labels.append(label)

        try:
            title = ' || '.join(labels)
            #用'||'连接labels，作为title

            self.vis.images(images, 
            	            nrow=self.ncols,#一行有几张图片，也就是列数/分组方式 
            	            win=win_id,
                            padding=5, 
                            opts=dict(title=title))

        except ConnectionError:
        	#连接错误
            self.throw_visdom_connection_error()
        
    # utils
    def tensor2im(self, input_image, imtype=np.uint8):
    	#tensor->numpy->image->(process->)numpy

        if isinstance(input_image, torch.Tensor):
            image_tensor = input_image.data
            #用data不会计算梯度
        else:
        	#非tensor，不处理
            return input_image
        image_numpy = image_tensor[0].cpu().float().numpy()
        #？？？data[0]

        im = self.numpy2im(image_numpy, imtype).resize((80, 80), Image.ANTIALIAS)
        #AntiAlias是抗锯齿,80*80是图片大小

        #image->numpy
        return np.array(im)
        
    def numpy2im(self, image_numpy, imtype=np.uint8):

        if image_numpy.shape[0] == 1:
            image_numpy = np.tile(image_numpy, (3, 1, 1))  
            #如果是灰度图，就把灰度图变成三通道的灰色图
            #tile是在某个维度上重复的意思
        
        #image_numpy = np.transpose(image_numpy, (1, 2, 0)) * 255.0
        # input should be [0, 1]
        # print(image_numpy.shape)
        image_numpy = (np.transpose(image_numpy, (1, 2, 0)) / 2. + 0.5) * 255.0
        #把像素变为[0,255],图片的数组都要变成这样
        #input should be [-1,1]

        image_numpy = image_numpy.astype(imtype)
        
        return Image.fromarray(image_numpy)