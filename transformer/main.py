import os
import sys
import shutil
from transformer import transform
from cutter import cut
from rebuilder import rebuild
from combiner import combine
from ausgetter import ausget




dirPath=sys.argv[1]
baseName=sys.argv[2]
fileName=sys.argv[3]
num = int(sys.argv[4])
sys.argv=[sys.argv[0],]

unhappyAus=[0.0,0.0,0.0,0.83,0.00,0.14, 0.00,0.00,0.00,0.00,0.97, 0.55 , 0.26,0.13,0.00,0.00 ,0.0]
happyAus=[0.0,0.0,0.0, 0.4,1.31,0.0 ,0.08 ,0.7 ,2.18,0.75,0.0 , 0.08 ,0.16 ,0.0 ,1.25,0.73 ,0.0]
ausList=[happyAus,unhappyAus,]

happyPath=os.path.join(dirPath,baseName,'happy.gif')
unhappyPath=os.path.join(dirPath,baseName,'unhappy.gif')
gifList=[happyPath,unhappyPath,]

filePath=os.path.join(dirPath,baseName,fileName)
headPath=os.path.join(dirPath,baseName,'head.png')
srcPath=os.path.join(dirPath,baseName,'src')
targetPath=os.path.join(dirPath,baseName,'target')
ausPath=os.path.join(dirPath,baseName,'aus.pkl')

left,top=cut(filePath,headPath)
# cutter

ausget(os.path.join(dirPath,baseName))
# ausgetter

for i in range(len(ausList)):
	if(not os.path.exists(srcPath)):
		os.mkdir(srcPath)
	print(num,headPath,srcPath,ausPath,ausList[i])
	print("***********************")
	print('\n')
	transform(num,headPath,srcPath,ausPath,ausList[i])
	# transformer


	if(not os.path.exists(targetPath)):
		os.mkdir(targetPath)
	rebuild(num,left,top,filePath,srcPath,targetPath)
	# rebuilder


	combine(num,targetPath,gifList[i])
	# combine

shutil.rmtree(srcPath)
shutil.rmtree(targetPath)
