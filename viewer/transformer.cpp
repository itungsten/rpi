#include "transformer.h"
#include "widget.h"
#include "ui_widget.h"
#include<QKeyEvent>
#include<QImage>
#include<QDebug>
#include<iostream>
#include"conf.h"


Transformer::Transformer()
{

}
int Transformer::classifier(){
    return 0;
}

void Transformer::transform(QString path){
    info.setFile(path);
    char baseName[BUF_SIZE];
    strcpy(baseName,info.baseName().toStdString().c_str());
    char fileName[BUF_SIZE];
    strcpy(fileName,info.fileName().toStdString().c_str());
    char * argv[]={PYTHONPATH,CMDBASEPATH,WAREHOUSEPATH,baseName,fileName,"10",nullptr};
    char * env[]={"LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1",nullptr};
    posix_spawn(nullptr,PYTHONPATH,nullptr,nullptr,argv,env);
}
