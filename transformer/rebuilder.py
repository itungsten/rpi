def rebuild(num,left,top,personPath,srcPath,targetPath):
    import os
    from PIL import Image
    for i in range (num):
        personIMA = Image.open(personPath)
       	framePath= os.path.join(srcPath,str(i+1)+".png")
        frmaeIMA = Image.open(framePath)
        personIMA.paste(frmaeIMA,(left,top))
        framePath= os.path.join(targetPath,str(i+1)+".png")
        personIMA.save(framePath)

if __name__=='__main__':
	rebuild(3,200,58,'D:/magicAlbum/sharePool/person.png','D:/magicAlbum/sharePool/src','D:/magicAlbum/sharePool/target')