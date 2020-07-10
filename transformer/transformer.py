def transform(num,infile,outfile,ausPath,tarAus):
	import ganimation.gan as gan
	gan.test(num,infile,outfile,ausPath,tarAus)

if __name__=='__main__':
	transform(10,'./head.png','./src','',None)