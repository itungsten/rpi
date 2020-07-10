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

void Transformer::transform(QString path){
    info.setFile(path);
    char baseName[BUF_SIZE];
    strcpy(baseName,info.baseName().toStdString().c_str());
    char fileName[BUF_SIZE];
    strcpy(fileName,info.fileName().toStdString().c_str());
    //baseName和fileName都是为了调用posix_spawn做的准备

    char * argv[]={PYTHONPATH,TRANSFORMPATH,WAREHOUSEPATH,baseName,fileName,"10",nullptr};
    char * env[]={"LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1",nullptr};
    posix_spawn(nullptr,PYTHONPATH,nullptr,nullptr,argv,env);//启动一个子进程
    //argv 和 env 的作用是提供程序参数(argv)和环境变量(env)
}
