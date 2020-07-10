from .base_dataset import BaseDataset
import os
import random
import numpy as np


class CelebADataset(BaseDataset):
    """
    继承自BaseDataSet类
    主要负责重写方法
    """
    def __init__(self,opt):
        super(CelebADataset, self).__init__(opt)
        #父类初始化

    def get_aus_by_path(self, img_path):
        assert os.path.isfile(img_path), "Cannot find image file: %s" % img_path
        #判断是不是一个图片文件的路径

        img_id = str(os.path.splitext(os.path.basename(img_path))[0])
        #basename中包含扩展名，这里splitext取[0]是为了取基础名作为key

 		
        # print(self.aus_dict[img_id])
        # return self.aus_dict[img_id]   
        return self.aus_dict[img_id] / 5.0   
        # norm to [0, 1],本身是[0,5]

    def make_dataset(self):
        # return all image full path in a list
        imgs_path = []
        assert os.path.isfile(self.imgs_name_file), "%s does not exist." % self.imgs_name_file
        #检查图片id文件是否存在

        with open(self.imgs_name_file, 'r') as f:
            lines = f.readlines()
            imgs_path = [os.path.join(self.imgs_dir, line.strip()) for line in lines]
            #全路径
            imgs_path = sorted(imgs_path)
            #完全有序
        return imgs_path

    def __getitem__(self, index):
        img_path = self.imgs_path[index]
        #index->path

        # load source image
        src_img = self.get_img_by_path(img_path)
        #返回的是转换后的图片
        src_img_tensor = self.img2tensor(src_img)
        #transformer就是图片转换器
        src_aus = self.get_aus_by_path(img_path)

        # load target image
        tar_img_path = random.choice(self.imgs_path)
        #choice是从可迭代序列中随机选择一个作为target

        # laugh_img='000050.jpg'
        laugh_img='target.jpg'
        laugh_img=os.path.join(self.imgs_dir,laugh_img)
        tar_img_path=laugh_img
        #用户手动指定target图片


        tar_img = self.get_img_by_path(tar_img_path)
        tar_img_tensor = self.img2tensor(tar_img)
        tar_aus = self.get_aus_by_path(tar_img_path)

        if self.is_train and self.opt.aus_noise:
            tar_aus = tar_aus + np.random.uniform(-0.1, 0.1, tar_aus.shape)
            #添加噪音，训练时

        # print(tar_aus)
        # record paths for debug and test usage
        data_dict = {'src_img':src_img_tensor, 'src_aus':src_aus, 'src_path':img_path,'tar_img':tar_img_tensor, 'tar_aus':tar_aus, \
                         'tar_path':tar_img_path}

        return data_dict
