import argparse
import torch
import os
from datetime import datetime
import time 
import random
import numpy as np 
import sys


class Options(object):
    def __init__(self):
        super(Options, self).__init__()#传入自己的类名，和对象，调用父的构造函数
        
    def initialize(self):
        try:
            parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        except Exception as e:
            print(repr(e))
            import traceback
            traceback.print_exc()
        else:
            pass

        parser.add_argument('--ckpt_dir', type=str, default='/home/pi/Desktop/magicAlbum/transformer/ganimation/ckpts/emotionNet/ganimation/190327_160828', help='directory to save check points.')
        #保存checkpoints的目录(记录了各个epoch内容)
        parser.add_argument('--results', type=str, default="D:/magicAlbum/sharePool/src", help='save test results to this path.')
        #保存测试结果文件地址
        parser.add_argument('--data_root',default='D:/magicAlbum/sharePool/head.png', help='paths to data set.')
        #数据集路径


        parser.add_argument('--mode', type=str, default='test', help='Mode of code. [train|test]')
        #训练或者测试
        parser.add_argument('--model', type=str, default='ganimation', help='[ganimation|stargan], see model.__init__ from more details.')
        #选择使用的模型
        parser.add_argument('--lucky_seed', type=int, default=0, help='seed for random initialize, 0 to use current time.')
        #选择随机数种子，提高复现性
        parser.add_argument('--visdom_env', type=str, default="main", help='visdom env.')
        #可视化服务visdom使用的窗口名字
        parser.add_argument('--visdom_port', type=int, default=8097, help='visdom port.')
        #visdom服务端口
        parser.add_argument('--visdom_display_id', type=int, default=1, help='set value larger than 0 to display with visdom.')
        #？？？
        parser.add_argument('--interpolate_len', type=int, default=5, help='interpolate length for test.')
        parser.add_argument('--no_test_eval', action='store_true', help='do not use eval mode during test time.')
        #设置测试时不评估
        parser.add_argument('--save_test_gif', action='store_true', help='save gif images instead of the concatenation of static images.')
        #将默认设置的静态拼接图片变成动态图
        parser.add_argument('--imgs_dir', type=str, default="imgs", help='path to image')
        #数据集下纯图片文件夹的路径
        parser.add_argument('--aus_pkl', type=str, default="aus_openface.pkl", help='AUs pickle dictionary.')
        #对数据集中图片提取的AU向量（17维）的字典序列化之后的pickle文件。内容是一个字典，key是图片名，value是AU向量。
        parser.add_argument('--train_csv', type=str, default="train_ids.csv", help='train images paths')
        #内含数据集中用于训练的图片的id们
        parser.add_argument('--test_csv', type=str, default="test_ids.csv", help='test images paths')
        #内含数据集中用于测试的图片的id们
        parser.add_argument('--batch_size', type=int, default=2, help='input batch size.')
        #批大小，不可为1，会出现维度问题
        parser.add_argument('--serial_batches', action='store_true', help='if specified, input images in order.')
        #设置后，不进行shuffle
        parser.add_argument('--n_threads', type=int, default=6, help='number of workers to load data.')
        #加载数据时的线程数
        parser.add_argument('--max_dataset_size', type=int, default=float("inf"), help='maximum number of samples.')
        #最多使用的图片数
        parser.add_argument('--resize_or_crop', type=str, default='none', help='Preprocessing image, [resize_and_crop|crop|none]')
        #图像预处理（图像增强），在windows下设置none会出错，这是pickle在windows下对默认none时使用lambda函数的不支持造成的
        parser.add_argument('--load_size', type=int, default=148, help='scale image to this size.')
        #预处理时resize的size
        parser.add_argument('--final_size', type=int, default=128, help='crop image to this size.')
        #预处理时crop后的size
        parser.add_argument('--no_flip', action='store_true', help='if specified, do not flip image.')
        #设置预处理不进行图像翻转
        parser.add_argument('--aus_noise', action='store_true', help='if specified, add noise to target AUs.')
        #有关目标AU向量的噪声
        parser.add_argument('--gpu_ids', type=str, default='-1', help='gpu ids, eg. 0,1,2; -1 for cpu.')
        #使用的gpu，默认使用gpu0，可以使用多个，设置-1使用cpu
        parser.add_argument('--load_epoch', type=int, default=30, help='load epoch; 0: do not load')
        #？？？设置加载的epoch，0是不加载
        parser.add_argument('--log_file', type=str, default="logs.txt", help='log loss')
        #损失日志的路径
        parser.add_argument('--opt_file', type=str, default="opt.txt", help='options file')
        #配置文件的路径

        # train options 
        parser.add_argument('--img_nc', type=int, default=3, help='image number of channel')
       	#图片通道数
        parser.add_argument('--aus_nc', type=int, default=17, help='aus number of channel')
       	#AU向量的维度
        parser.add_argument('--ngf', type=int, default=64, help='ngf')
       	#生成网络中第一层的特征数（网络中倍增
        parser.add_argument('--ndf', type=int, default=64, help='ndf')
       	#判别网络中第一层的特征数（网络中倍增
        parser.add_argument('--use_dropout', action='store_true', help='if specified, use dropout.')
       	#使用dropout，目的是降低过拟合风险
        
        parser.add_argument('--gan_type', type=str, default='wgan-gp', help='GAN loss [wgan-gp|lsgan|gan]')
        #gan对抗损失的具体实现
        parser.add_argument('--init_type', type=str, default='normal', help='network initialization [normal|xavier|kaiming|orthogonal]')
        #神经网络参数初始化策略
        parser.add_argument('--init_gain', type=float, default=0.02, help='scaling factor for normal, xavier and orthogonal.')
        #？？？初始化使用的比例因子？？？
        parser.add_argument('--norm', type=str, default='instance', help='instance normalization or batch normalization [batch|instance|none]')
        #选择使用的正则化方式

        parser.add_argument('--beta1', type=float, default=0.5, help='momentum term of adam')
        #配置adma优化器的动量项
        parser.add_argument('--lr', type=float, default=0.0001, help='initial learning rate for adam')
        #优化器的初始学习率
        parser.add_argument('--lr_policy', type=str, default='lambda', help='learning rate policy: lambda|step|plateau|cosine')
        #学习率变换策略
        parser.add_argument('--lr_decay_iters', type=int, default=50, help='multiply by a gamma every lr_decay_iters iterations')
        #学习率衰减间隔
        parser.add_argument('--epoch_count', type=int, default=1, help='the starting epoch count, we save the model by <epoch_count>, <epoch_count>+<save_latest_freq>, ...')
        #设置开始时是第几个epoch，便于保存chekcpoint和进行tune
        parser.add_argument('--niter', type=int, default=20, help='# of iter at starting learning rate')
        #保持初始学习率的迭代次数
        parser.add_argument('--niter_decay', type=int, default=10, help='# of iter to linearly decay learning rate to zero')
        #线性下降学习率到零的次数

        # loss options 
        #各种损失项的权重
        parser.add_argument('--lambda_dis', type=float, default=1.0, help='discriminator weight in loss')
        parser.add_argument('--lambda_aus', type=float, default=160.0, help='AUs weight in loss')
        parser.add_argument('--lambda_rec', type=float, default=10.0, help='reconstruct loss weight')
        parser.add_argument('--lambda_mask', type=float, default=0, help='mse loss weight')
        parser.add_argument('--lambda_tv', type=float, default=0, help='total variation loss weight')
        parser.add_argument('--lambda_wgan_gp', type=float, default=10., help='wgan gradient penalty weight')

        # frequency options
        parser.add_argument('--train_gen_iter', type=int, default=5, help='train G every n interations.')
        #每多少次迭代训练一次生成器
        parser.add_argument('--print_losses_freq', type=int, default=100, help='print log every print_freq step.')
        #打印损失的频率
        parser.add_argument('--plot_losses_freq', type=int, default=20000, help='plot log every plot_freq step.')
        #visdom显示损失的频率
        parser.add_argument('--sample_img_freq', type=int, default=2000, help='draw image every sample_img_freq step.')
        #visdom画图的频率
        parser.add_argument('--save_epoch_freq', type=int, default=2, help='save checkpoint every save_epoch_freq epoch.')
        #每多少个epoch保存一个checkpoints

        return parser

    def parse(self):
        """解析参数"""
        
        parser=self.initialize()#初始化默认值和参数项
        # print("HHH")	

        parser.set_defaults(name=datetime.now().strftime("%y%m%d_%H%M%S"))
        #设置name参数默认为格式化后的当前时间
        opt = parser.parse_args()
        #opt是解析器解析参数后的结果,应该是在这个函数里面读入的命令行参数

        dataset_name = os.path.basename(opt.data_root.strip('/'))
        #处理数据集路径 先去掉两头的/，再取基本名


        # update checkpoint dir
        if opt.mode == 'train' and opt.load_epoch == 0:
        	#在训练时ckptr_dir自动生成
            opt.ckpt_dir = os.path.join(opt.ckpt_dir, dataset_name, opt.model, opt.name)
            #该函数把各个组件按路径的方式组合 e.g.（ckpts\celebA\ganimation\190327_161852）
            if not os.path.exists(opt.ckpt_dir):
                os.makedirs(opt.ckpt_dir)
            #如果不存在，创建



        # if test, disable visdom, update results path
        if opt.mode == "test":
        	#测试环节：取消visdom，生成results
        	#修正参数之间不和谐的地方，提高鲁棒性

            opt.visdom_display_id = 0
            # opt.results = os.path.join(opt.results, "%s_%s_%s" % (dataset_name, opt.model, opt.load_epoch))
            #e.g. results\celebA_ganimation_30
            if not os.path.exists(opt.results):
                os.makedirs(opt.results)
            #如果不存在，创建


        # set gpu device
        str_ids = opt.gpu_ids.split(',')
        opt.gpu_ids = []
        for str_id in str_ids:
            cur_id = int(str_id)
            if cur_id >= 0:
                opt.gpu_ids.append(cur_id)
        if len(opt.gpu_ids) > 0:
            torch.cuda.set_device(opt.gpu_ids[0])
            #有多个默认只使用第一个gpu设备

        # set seed 
        if opt.lucky_seed == 0:
            opt.lucky_seed = int(time.time())
        #如果没有设置，用系统时间作为种子

        random.seed(a=opt.lucky_seed)
        np.random.seed(seed=opt.lucky_seed)
        torch.manual_seed(opt.lucky_seed)
       	#设置了几处诶

        if len(opt.gpu_ids) > 0:
        	#使用cudnn神经网络加速库,并设置一些奇怪的东西和随机数种子
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            torch.cuda.manual_seed(opt.lucky_seed)
            torch.cuda.manual_seed_all(opt.lucky_seed)
            
        # write command to file
        script_dir = opt.ckpt_dir 
        #和checkpoints一个目录下（有30_net_dis.pth 30_net_gen.pth opt.txt run_script.sh)


        return opt


        with open(os.path.join(script_dir, "run_script.sh"), 'a+') as f:
            f.write(    "[%5s][%s]python %s\n"    %    (opt.mode, opt.name, ' '.join(sys.argv))    )
            #sys.argv全都是字符串，包括--和-
        #把每次对该checkpoints运行的命令记录下来，比如说微调啊什么的

        # print and write options file
        msg = ''
        #空初始化
        msg += '------------------- [%5s][%s]Options --------------------\n' % (opt.mode, opt.name)
        for k, v in sorted(vars(opt).items()):
            comment = ''
            default_v = parser.get_default(k)
            if v != default_v:
                comment = '\t[default: %s]' % str(default_v)
            msg += '{:>25}: {:<30}{}\n'.format(str(k), str(v), comment)
        msg += '--------------------- [%5s][%s]End ----------------------\n' % (opt.mode, opt.name)
        
        print(msg)
        with open(os.path.join(script_dir, "opt.txt"), 'a+') as f:
            f.write(msg + '\n')
        #打印和保存配置信息
        return opt
