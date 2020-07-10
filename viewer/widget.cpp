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

    setWindowFlags(Qt::FramelessWindowHint);//设置无边框，从而自定义边框，提升美观度和跨平台一致性
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

    }//配置预览界面按钮的图标和快捷键

    connect(ui->leftBtn,&FlatCtrlButton::signalClicked,[=](){
        leftPic();//左切换图片
    });
    connect(ui->rgtBtn,&FlatCtrlButton::signalClicked,[=](){
        rgtPic();//右切换图片
    });
    connect(ui->iconBtn->ui->pushBtn,&QPushButton::clicked,[=](){
        editor->load();//加载editor内容
        editor->move(this->x()+(this->width()-editor->width())/2,this->y());
        //固定editor相对位置(自定义，跨平台)
        editor->show();
    });
    connect(ui->fullBtn->ui->pushBtn,&QPushButton::clicked,[=](){
      full->showFullScreen();
      if(previewIndex==-1){//如果没有图片
          full->ui->label->setText("Hello        World"); return;
      }

      editor->target=editor->list[previewIndex];
      editor->now=new QMovie(editor->target);
      editor->now->start();
      full->ui->label->setFixedSize(getFullSize());
      full->ui->label->setScaledContents(true);
      full->ui->label->setMovie(editor->now);
      //呈现图片

      full->openPipe();//打开摄像头程序并利用管道通信
      timer->start(interval);//begin to count
    });
    connect(editor,&Editor::signalChangePic,[=](){
        flushPic();//退出Editor后刷新预览界面图片
    });
    connect(editor->ui->list,&QListWidget::itemDoubleClicked,[=](QListWidgetItem *item){
        //双击切换预览图片为----该item对应图片
        previewIndex=editor->ui->list->row(item);//更改索引
        editor->close();//调用closeEvent
    });
    connect(timer,&QTimer::timeout,[=](){//按时触发
        std::string line;
        getline(*(full->f),line);
        int val= stoi(line);
        //进程间通信

        QFileInfo info(editor->target);

        //目前只分了happy和unhappy两类，使用3和5代表
        if(full->lastCode==3&&val<=3)goto cont;
        if(full->lastCode==5&&val>3)goto cont;
        //no change

        if(full->anime!=nullptr)delete full->anime;
        switch(val){
        case 0:
        case 1:
        case 2:
        case 3:
            //unhappy
            full->lastCode=3;
            full->anime=new QMovie(QString(WAREHOUSEPATH)+info.baseName()+"/unhappy.gif");
            break;
        case 4:
        case 5:
            //happy
            full->lastCode=5;
            full->anime=new QMovie(QString(WAREHOUSEPATH)+info.baseName()+"/happy.gif");
            break;
        default:
            full->lastCode=5;
            full->anime=new QMovie(QString(WAREHOUSEPATH)+info.baseName()+"/happy.gif");
            break;
        }
        full->ui->label->setMovie(full->anime);
        full->anime->start();
        //呈现动画
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
    this->show();//显示窗体
}

Widget::~Widget()
{
    delete ui;
}

void Widget::flushPic()//退出Editor后刷新预览界面图片
{
    if(editor->list.size()==0){//没有图片预览
        editor->target="";
        previewIndex=-1;
        ui->movielbl->setText("Hello        World");
        setStatusBar();
        return;
    }
    if(previewIndex==-1||(previewIndex>(editor->list.size()-1))){
        previewIndex=0;//有图片，但是索引非法，更正索引为0
    }
    //呈现图片
    editor->target=editor->list[previewIndex];
    editor->now=new QMovie(editor->target);
    ui->movielbl->setMovie(editor->now);
    editor->now->start();

    setStatusBar();//更新状态栏
}

void Widget::leftPic()
{
    if(previewIndex>0){
        delete editor->now;
        --previewIndex;
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
        ++previewIndex;
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

void Widget::setStatusBar()//更新状态栏
{
    if(previewIndex==-1){//无图片默认显示版本号
        ui->statuslbl->setText("Version: "+version);
        return;
    }

    QFileInfo info(editor->list[previewIndex]);
    ui->statuslbl->setText(" Name: "+info.fileName()+"   Created:"+info.birthTime().toString("yyyy/MM/dd"));
    //否则显示文件的基本名和创建日期
}

QSize Widget::getFullSize()
{
    QPixmap first=editor->now->currentPixmap();//用以获取图片尺寸
    int sx,sy; //size of x，size of y
    double rate;//伸缩比例
    sy=(full->size()).height();//高度为屏幕高度
    rate=sy*1.0/first.height();//1.0转换为float  比例=屏幕高度/原高度
    sx=int(rate*first.width());//现在宽度=比例*原宽度
    return QSize(sx,sy);
}


void Widget::mouseMoveEvent(QMouseEvent *ev)
{
    if(ev->buttons()==Qt::LeftButton){//鼠标左键才移动
        int xmin=ui->iconBtn->pos().x()+ui->iconBtn->width();
        int xmax=ui->minBtn->pos().x();
        //点击处的位置设置在一个矩形内x:xmin~xmax，y:0~55

        if(ev->y()<=55&&ev->x()>=xmin&&ev->x()<=xmax){
           this->move(ev->globalX()-dis.width(),ev->globalY()-dis.height());
           //让窗口跟上鼠标
        }
    }
    return QWidget::mouseMoveEvent(ev);
}

void Widget::mousePressEvent(QMouseEvent *ev)
{
    if(ev->buttons()==Qt::LeftButton){//只有左键单点才能移动
        dis=QSize(ev->x(),ev->y());
        //记录相对距离，一般来说x，y都是相对父窗口的，故本来就是相对距离
    }
    return QWidget::mousePressEvent(ev);
}
