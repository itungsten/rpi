def ausget(dirPath):
    import sys
    import os
    from subprocess import run
    import pandas as pd
    import pickle
    headPath=os.path.join(dirPath,'head.png')
    run("/home/pi/openface/FaceLandmarkImg -aus -out_dir "+dirPath+" -f "+headPath+" >nul",shell=True)
    csvPath=os.path.join(dirPath,'head.csv')
    csvFile=pd.read_csv(csvPath)
    detailPath=os.path.join(dirPath,'head_of_details.txt')
    ausPath=os.path.join(dirPath,'aus.pkl')
    os.remove(csvPath)
    os.remove(detailPath)
    with open(ausPath, 'wb') as f:
        pickle.dump(csvFile.iloc[0][2:19],f)

if __name__=='__main__':
    ausget('D:/magicAlbum/warehouse/person')