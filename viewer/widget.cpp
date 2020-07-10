#include "widget.h"
#include "ui_widget.h"

#include "flatpushbutton.h"
#include "ui_flatpushbutton.h"

#include "flatctrlbutton.h"
#include "ui_flatctrlbutton.h"

#include "editor.h"
#include "ui_editor.h"

#include "fullscreen.h"
#include "ui_fullscreen.h"


#include<QPushButton>
#include<algorithm>
#include<QDebug>
#include<QPixmap>
#include<QMovie>
#include<QIcon>
#include<QMessageBox>
#include<QList>
#include<QListWidget>
#include<QListWidgetItem>
#include<QFileInfo>
#include<QDateTime>
#include<QLabel>

#include"conf.h"

Widget::Widget(QWidget *parent)
    : QWidget(parent)
    , ui(new Ui::Widget)
{
    ui->setupUi(this);
    full=new FullScreen(this);//创建full子窗口
    editor=new Editor(this);//创建editor子窗口
    timer=new QTimer();//创建计时触发器

    setWindowFlags(Qt::FramelessWindowHint);//设置无边框，从而自定义边框，提示美观度和跨平台一致性
    setStyleSheet("background-color:white;border:0px");//设置窗口整体风格
    setWindowIcon(QIcon(":/icons/picture.png"));//窗体图标
    ui->statuslbl->setText("Version: "+version);//状态栏默认显示版本号
    ui->titlelbl->setText("Magic Album");//设置title

    full->setStyleSheet("background-color:"+editor->background);//设置全屏窗口背景色

    ui->exitBtn->setStyleSheet("QPushButton:hover{background-color:red}"
                               "QPushButton:pressed{background-color:rgba(255,0,0,0.5)}"
                               "QPushButton:focus{outline:none;}");
    //单独设置退出按钮风格


    {
        ui->iconBtn->ui->pushBtn->setIcon(QIcon(":/icons/picture.png"));
        ui->iconBtn->ui->pushBtn->setIconSize((ui->iconBtn->size()/3)*2);
        ui->iconBtn->ui->pushBtn->setShortcut(QKeySequence("Ctrl+A"));

        ui->fullBtn->ui->pushBtn->setIcon(QIcon(":/icons/full.png"));
        ui->fullBtn->ui->pushBtn->setIconSize((ui->fullBtn->size()/4)*2);

        ui->leftBtn->ui->pushBtn->setIcon(QIcon(":/icons/back.png"));
        ui->leftBtn->ui->pushBtn->setIconSize((ui->leftBtn->ui->pushBtn->size()/5)*2);

        ui->rgtBtn->ui->pushBtn->setIcon(QIcon(":/icons/next.png"));
        ui->rgtBtn->ui->pushBtn->setIconSize((ui->rgtBtn->ui->pushBtn->size()/5)*2);

        ui->maxBtn->ui->pushBtn->setIcon(QIcon(":/icons/max.png"));
        ui->maxBtn->ui->pushBtn->setIconSize((ui->maxBtn->ui->pushBtn->size()/5)*2);

        ui->minBtn->ui->pushBtn->setIcon(QIcon(":/icons/min.png"));
        ui->minBtn->ui->pushBtn->setIconSize((ui->minBtn->ui->pushBtn->size()/5)*2);

        ui->exitBtn->ui->pushBtn->setIcon(QIcon(":/icons/cross.png"));
        ui->exitBtn->ui->pushBtn->setIconSize((ui->exitBtn->ui->pushBtn->size()/5)*2);
        ui->exitBtn->ui->pushBtn->setShortcut(QKeySequence("Ctrl+C"));

    }//配置预览界面七大按钮的图标和快捷键


    connect(ui->leftBtn,&FlatCtrlButton::signalClicked,[=](){
        leftPic();
        //连接左切换
    });
    connect(ui->rgtBtn,&FlatCtrlButton::signalClicked,[=](){
        rgtPic();
        //连接右切换
    });
    connect(ui->iconBtn->ui->pushBtn,&QPushButton::clicked,[=](){
        editor->renew();//更新editor内容
        editor->move(this->x()+(this->width()-editor->width())/2,this->y());
        //固定editor相对位置（自定义，跨平台）
        editor->show();
    });
    connect(ui->fullBtn->ui->pushBtn,&QPushButton::clicked,[=](){
      full->showFullScreen();
      full->setWindowState(full->windowState() | Qt::WindowFullScreen);
      full->disPoint.setY(0);
      full->disPoint.setX((full->width()-full->height())/2);
      if(previewIndex==-1){
          //如果没有图片
          full->ui->label->setText("Hello        World");
//          qDebug()<<full->size().height()<<" no pic interface"<<endl;
//          qDebug()<<full->size().width()<<" no pic interface"<<endl;
          //全屏后刷新size，设置disPoint，为了用户交互图的坐标变换
          return;
      }


      editor->target=editor->list[previewIndex];

      editor->now=new QMovie(editor->target);
      editor->now->start();
      full->ui->label->setMovie(editor->now);
      full->anima=nullptr;
      full->ui->label->setFixedSize(getFullSize());
      full->ui->label->setScaledContents(true);
//      qDebug()<<full->ui->label->size();
      //设置movie并开始播放，以刷新第一张Pixmap

//      QFileInfo info(editor->target);
//      full->anima=new QMovie(QString(WAREHOUSEPATH)+info.baseName()+"/result.gif");
//      full->ui->label->setMovie(full->anima);
//      full->anima->start();
      //显示全屏窗口并且计时

      full->openPipe();
      timer->start(interval);
//      qDebug()<<full->size().height()<<" pic interface"<<endl;
//      qDebug()<<full->size().width()<<"  pic interface"<<endl;
    });
    connect(editor,&Editor::signalChangePic,[=](){
        flushPic();
        //刷新预览界面图片
    });
    connect(editor->ui->list,&QListWidget::itemDoubleClicked,[=](QListWidgetItem *item){
        //双击切换预览图片为----该item对应图片
        previewIndex=editor->ui->list->row(item);//更改索引
        editor->close();//调用closeEvent
    });
    connect(timer,&QTimer::timeout,[=](){
        std::string line;
        getline(*(full->f),line);
        int val= stoi(line);

        QFileInfo info(editor->target);
        if(full->lastCode==3&&val<=3)goto cont;
        if(full->lastCode==5&&val>3)goto cont;
        if(full->anima!=nullptr)delete full->anima;
        switch(val){
        case 0:
        case 1:
        case 2:
        case 3:
            full->lastCode=3;
            full->anima=new QMovie(QString(WAREHOUSEPATH)+info.baseName()+"/unhappy.gif");
            break;
        case 4:
        case 5:
        case 6:
            full->lastCode=5;
            full->anima=new QMovie(QString(WAREHOUSEPATH)+info.baseName()+"/happy.gif");
            break;
        default:
            full->lastCode=5;
            full->anima=new QMovie(QString(WAREHOUSEPATH)+info.baseName()+"/happy.gif");
            break;
        }
        full->ui->label->setMovie(full->anima);
        full->anima->start();
        cont:
        qDebug()<<"receive msg:"<<val<<endl;
    });

    connect(ui->exitBtn->ui->pushBtn,&QPushButton::clicked,[=](){
        close();
    });
    connect(ui->minBtn->ui->pushBtn,&QPushButton::clicked,[=](){
        showMinimized();
    });
    connect(ui->maxBtn->ui->pushBtn,&QPushButton::clicked,[=](){
        //两种状况
        if(isMaximized()){
            showNormal();
            ui->maxBtn->ui->pushBtn->setIcon(QIcon(":/icons/max.png"));
        }
        else{
            showMaximized();
            ui->maxBtn->ui->pushBtn->setIcon(QIcon(":/icons/restore.png"));
        }
    });



    this->show();//自动显示窗体
}

Widget::~Widget()
{
    delete ui;
}

void Widget::flushPic()
{
    if(editor->list.size()==0){
        //没有图片预览
        editor->target="";
        previewIndex=-1;
        ui->movielbl->setText("Hello        World");
        setStatusBar();
        return;
    }
    if(previewIndex==-1||(previewIndex>(editor->list.size()-1))){
        previewIndex=0;
        //有图片，但是索引非法
    }
    editor->target=editor->list[previewIndex];
    editor->now=new QMovie(editor->target);
    ui->movielbl->setMovie(editor->now);
    editor->now->start();
//    ui->movielbl->update();
    setStatusBar();
}

void Widget::leftPic()
{
    if(previewIndex>0){
        delete editor->now;
        previewIndex--;
        editor->target=editor->list[previewIndex];
        editor->now=new QMovie(editor->target);
        ui->movielbl->setMovie(editor->now);
        editor->now->start();
    }
    else{
        QMessageBox::information(this,"提示","no more");
    }
    setStatusBar();
}
void Widget::rgtPic()
{
    if(previewIndex<(editor->list.size()-1)){
        delete editor->now;
        previewIndex++;
        editor->target=editor->list[previewIndex];
        editor->now=new QMovie(editor->target);
        ui->movielbl->setMovie(editor->now);
        editor->now->start();
    }
    else{
        QMessageBox::information(this,"提示","no more");
    }
    setStatusBar();
}

void Widget::setStatusBar()
{
    if(previewIndex==-1){
        //无图片默认显示版本号
        ui->statuslbl->setText("Version: "+version);
        return;
    }

    QFileInfo info(editor->list[previewIndex]);
    //否则显示文件的基本名和创建日期
    ui->statuslbl->setText(" Name: "+info.fileName()+"   Created:"+info.birthTime().toString("yyyy/MM/dd"));
}

QSize Widget::getFullSize()
{
    QPixmap first=editor->now->currentPixmap();//用以获取图片尺寸
    int sx,sy; //size of x，size of y
    double rate;//伸缩比例
    sy=(full->size()).height();//高度为屏幕高度
    rate=sy*1.0/first.height();//1.0转换为float  比例=屏幕高度/原高度
    sx=int(rate*first.width());//现在宽度=比例*原宽度
    return QSize(sx,sy);//打包
}


void Widget::mouseMoveEvent(QMouseEvent *ev)
{
    if(ev->buttons()==Qt::LeftButton){
        //鼠标左键才移动

        int xmin=ui->iconBtn->pos().x()+ui->iconBtn->width();
        int xmax=ui->minBtn->pos().x();
        //点击范围设置在一个矩形内xmin~xmax，0~55

        if(ev->y()<=55&&ev->x()>=xmin&&ev->x()<=xmax){
            //让窗口跟上鼠标
           this->move(ev->globalX()-dis.width(),ev->globalY()-dis.height());
        }
    }
    return QWidget::mouseMoveEvent(ev);//其余 从父
}

void Widget::mousePressEvent(QMouseEvent *ev)
{
    if(ev->buttons()==Qt::LeftButton){
        //只有左键单点才能移动

        dis=QSize(ev->x(),ev->y());
        //记录相对距离，一般来说x，y都是相对父窗口的，故本来就是相对距离
    }
    return QWidget::mousePressEvent(ev);//其余 从父
}
