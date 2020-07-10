import torch
import os
from PIL import Image
import random
import numpy as np
import pickle
import torchvision.transforms as transforms

from .celeba import CelebADataset
from .base_dataset import BaseDataset


def create_dataloader(opt):
    #用配置创建一个DataLoader，按配置有默认两种选择
    return DataLoader(opt)


class DataLoader:
    #dataloader决定是用CelebA还是BaseDataSet
    #emotion和celeb都用CelebA;作者未定义的数据集就是用BaseDataSet，需要重写

    def __init__(self,opt):
    	#无父类，自己初始化
        self.initialize(opt)

    def initialize(self, opt):
        self.opt = opt
        self.dataset = self.create_dataset()
        self.dataloader = torch.utils.data.DataLoader(
            self.dataset,
            batch_size=opt.batch_size,
            shuffle=not opt.serial_batches,
            #是否随机化
            num_workers=int(opt.n_threads)
            #加载数据时的线程数
        )

    def create_dataset(self):
        # specify which dataset to load here
        loaded_dataset = os.path.basename(self.opt.data_root.strip('/')).lower()
        if 'celeba' in loaded_dataset or 'emotion' in loaded_dataset or 'dup' in loaded_dataset:
            dataset = CelebADataset(self.opt)
        else:
            dataset = BaseDataset(self.opt)
        return dataset

    def name(self):
        return self.dataset.name() + "_Loader"

    def __len__(self):
        return min(len(self.dataset), self.opt.max_dataset_size)
        #有max_dataset_size的限制

    def __iter__(self):
    	#迭代器的魔法命令

        for i, data in enumerate(self.dataloader):
        	#dataloader通过迭代体现出loader的性质
            if i * self.opt.batch_size >= self.opt.max_dataset_size:
                break
            yield data
            #迭代器的标志语法
