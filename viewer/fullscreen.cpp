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
    //设置escape退出全屏，并调用父类事件
    if(event->key()==Qt::Key_Escape||event->key()==Qt::Key_Q){
        Widget* ptr=static_cast<Widget*>(this->parent());//父对象指针
        if(ptr->previewIndex!=-1){
            ptr->ui->movielbl->setMovie(ptr->editor->now);
            //更新预览界面
        }
        ptr->timer->stop(); //停止计时
        closePipe();
        if(child_pid!=-1)kill(child_pid,SIGABRT);
        hide();//隐藏
    }
    return QWidget::keyReleaseEvent(event);
}

void FullScreen::mousePressEvent(QMouseEvent *ev)
{
      return QWidget::mousePressEvent(ev);
}
void FullScreen::mouseMoveEvent(QMouseEvent *ev){
      return QWidget::mouseMoveEvent(ev);
}

void FullScreen::mouseReleaseEvent(QMouseEvent *ev)
{

    return QWidget::mouseReleaseEvent(ev);
}

bool FullScreen::openPipe()
{
    mkfifo(FIFOPATH,0777);
//    qDebug()<<1;
    char * arg[]={PYTHONPATH,CLIENTPATH,nullptr};
    char * env[]={"LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1",nullptr};
//    qDebug()<<2;
    posix_spawn(&child_pid,PYTHONPATH,nullptr,nullptr,arg,env);
//    qDebug()<<3;
    f=new ifstream(FIFOPATH);
//    qDebug()<<4;
    return true;
}
void FullScreen::closePipe()
{
    f->close();
    system("rm -rf " FIFOPATH);
}
