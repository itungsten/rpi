def combine(num,src_path,saved_path):
    import imageio
    from PIL import Image
    import numpy as np
    import os
    imgs_numpy_list = []
    
    for i in range(num):
        cur_path=os.path.join(src_path,"%d.png" %(i+1))
        cur_numpy = np.array(Image.open(cur_path))
        #转化为numpy

        imgs_numpy_list.extend([cur_numpy for _ in range(3)])
        #复制三份，为了延时
    imageio.mimsave(saved_path, imgs_numpy_list,'GIF-PIL')
    return len(imgs_numpy_list)
    
if __name__=='__main__':
    combine(3,'D:/magicAlbum/sharePool/target','D:/magicAlbum/sharePool/result.gif')
