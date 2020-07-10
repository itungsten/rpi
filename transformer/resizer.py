import PIL
import os
from PIL import Image
if __name__=='__main__':
	root = 'wzr.jpg'
	pic = Image.open(root)
	(x,y) = pic.size
	x_s=300
	y_s=int(y*x_s/x)
	pic = pic.resize((x_s, y_s))
	pic.save('resized.jpg')