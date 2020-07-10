#include "fullscreen.h"
#include "ui_fullscreen.h"
#include "widget.h"
#include "ui_widget.h"
#include<QKeyEvent>
#include<QImage>
#include<QDebug>
#include<string>
#include<iostream>
#include<fstream>
#include"conf.h"
using namespace std;



FullScreen::FullScreen(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::FullScreen)
{
    ui->setupUi(this);
    setWindowFlags(Qt::Window);//设置相对独立样式
}

FullScreen::~FullScreen()
{
    delete ui;
}

void FullScreen::keyReleaseEvent(QKeyEvent *event)
{
    //设置escape&Q退出全屏
    if(event->key()==Qt::Key_Escape||event->key()==Qt::Key_Q){
        Widget* ptr=static_cast<Widget*>(this->parent());//父对象指针
        if(ptr->previewIndex==-1){
            hide();return;
        }
        ptr->ui->movielbl->setMovie(ptr->editor->now);//更新预览界面
        ptr->timer->stop(); //停止计时
        closePipe();//关闭通信管道
        if(child_pid!=-1)kill(child_pid,SIGABRT);//关闭摄像头进程
        if(anime)delete anime; anime=nullptr; //清理动画
        hide();//隐藏全屏界面
    }
    return QWidget::keyReleaseEvent(event);
}

bool FullScreen::openPipe()
{
    mkfifo(FIFOPATH,0777); //创建有名管道
    char * arg[]={PYTHONPATH,CLIENTPATH,nullptr};//程序参数
    char * env[]={"LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1",nullptr};//环境变量
    posix_spawn(&child_pid,PYTHONPATH,nullptr,nullptr,arg,env);//启动子进程
    f=new ifstream(FIFOPATH);//作为读端打开有名管道
    return true;
}
void FullScreen::closePipe()
{
    f->close();//关闭有名管道
    system("rm -rf " FIFOPATH);//删除有名管道
}
