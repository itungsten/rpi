import torch
import os
from PIL import Image
import random
import numpy as np
import pickle
import torchvision.transforms as transforms



class BaseDataset(torch.utils.data.Dataset):
    """继承torch里面的基础Dataset类"""

    def __init__(self,opt):
        super(BaseDataset, self).__init__()
        #父类初始化
        self.initialize(opt)
        #根据配置初始化

    def initialize(self, opt):
        self.opt = opt
        #copy配置

        self.imgs_dir = os.path.join(self.opt.data_root, self.opt.imgs_dir)
        #图片文件夹位置

        self.is_train = (self.opt.mode == "train")
        #是否是训练

        filename = self.opt.train_csv if self.is_train else self.opt.test_csv
        self.imgs_name_file = os.path.join(self.opt.data_root, filename)
        #打开的id文件名字
        self.imgs_path = self.make_dataset()
        #加载各图片路径

        #加载AU向量字典
        aus_pkl_file = os.path.join(self.opt.data_root, self.opt.aus_pkl)
        self.aus_dict = self.load_dict(aus_pkl_file)

        #加载图片变换器(image -> tensor)
        self.img2tensor = self.img_transformer()

    def name(self):
    	#名称
        return os.path.basename(self.opt.data_root.strip('/'))
        
    def make_dataset(self):
    	#会被重写
        return None

    def load_dict(self, pkl_path):
        saved_dict = {}
        with open(pkl_path, 'rb') as f:
        	#b是打开pickle序列号文件必要的
            # saved_dict = pickle.load(f, encoding='latin1')
            saved_dict = pickle.load(f)
            #encoding是latin1，我死了
        return saved_dict


    def get_img_by_path(self, img_path):
        assert os.path.isfile(img_path), "Cannot find image file: %s" % img_path
        #检查一下嘛

        img_type = 'L' if self.opt.img_nc == 1 else 'RGB'
        #L是灰度图，RGB是三通道

        return Image.open(img_path).convert(img_type)
        #返回打开并转化后的图片

    def get_aus_by_path(self, img_path):
    	#重写
        return None

    def img_transformer(self):
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

        return img2tensor

    def __len__(self):
    	#果然是用魔法命令
        return len(self.imgs_path)



    







