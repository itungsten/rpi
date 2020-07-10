#include "editor.h"
#include "ui_editor.h"
#include "widget.h"
#include "ui_widget.h"
#include<QFile>
#include<QFileInfo>
#include<QSpinBox>
#include<QFileDialog>
#include<QListWidget>
#include"transformer.h"
#include<QDebug>

#include"conf.h"

Editor::Editor(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::Editor)
{
    ui->setupUi(this);//布局
    inifile = new QFile(inipath);//new一个文件句柄的指针（对应imgs.ini配置文件）

    setWindowFlags(Qt::Window);//设置窗口样式，这是较为独立的一个样式
    setWindowModality(Qt::WindowModal);//模态窗口，阻塞消息队列

    //清除原有qss，并配置新样式
    this->setStyleSheet("");
    ui->line->setStyleSheet("background:rgb(195,195,195)");
    ui->newBtn->setStyleSheet("QPushButton:hover{background-color:rgb(215,215,215)}"
                               "QPushButton:pressed{background-color:rgb(195,195,195)}"
                                         "QPushButton{font: 9pt \"微软雅黑\";}"
                                         "QPushButton:focus{outline:none;}");
    ui->deleteBtn->setStyleSheet("QPushButton:hover{background-color:rgb(215,215,215)}"
                               "QPushButton:pressed{background-color:rgb(195,195,195)}"
                                         "QPushButton{font: 9pt \"微软雅黑\";}"
                                         "QPushButton:focus{outline:none;}");

    ui->list->setSelectionMode(QAbstractItemView::ExtendedSelection);
    //设置list控件可以按住ctrl多选

    //信号槽实现
    {
        connect(ui->list,&QListWidget::itemClicked,[=](QListWidgetItem* item){
            quickIndex=ui->list->row(item);
            QPixmap map(list[quickIndex]);
            ui->label->setPixmap(map);
        });
        //设置点击更新quickShow

        connect(ui->newBtn,&QPushButton::clicked,[=](){
            addItems();//添加item
            renewList();//保存配置文件
            quickShow();//更新quickshow(这是应对最初是NULL的情况)
        });

        connect(ui->deleteBtn,&QPushButton::clicked,[=](){
            deleteItems();
            renewList();
            quickShow();
        });

        void (QSpinBox::*myptr)(int)=&QSpinBox::valueChanged;//重载函数的函数指针
        connect(ui->left,myptr,[=](){
            //更新interval
            Widget* ptr=static_cast<Widget*>(this->parent());//对象树上父对象的指针
            ptr->interval=ui->left->value()*100;//msec
            if(ptr->interval==0)ptr->interval=100;//防止奇妙bug
        });

    }

}
Editor::~Editor()
{
    delete ui;
}
void Editor::addItems()
{
    QStringList names=QFileDialog::getOpenFileNames();//返回图片路径的数组,FileNames可以多选
    for(int i=0;i<names.size();++i){
        QFileInfo info(names[i]);
        if((info.suffix()=="gif")||(info.suffix()=="png")||(info.suffix()=="jpg")||(info.suffix()=="jpge")){
            //利用suffix筛选图片文件
            QString baseName=info.baseName();
            QDir dir;
            QString dirName=QString(WAREHOUSEPATH)+baseName;
            dir.mkdir(dirName);
            QString pathName=dirName+"/"+baseName+"."+info.suffix();
            QFile::copy(names[i],pathName);

//            auto a1=async(std::launch::async,&Transformer::transform,&transformer,pathName);
//            a1.wait();
            transformer.transform(pathName);
//            std::thread t(&Transformer::transform,&transformer,pathName);
//            WinExec("cmd /c activate t031 & python D:/cvtesst/capture2.py",SW_HIDE);
//            t.detach();
//            system("activate t031 & python D:/cvtesst/capture.py & pause");

            list.append(pathName);//向list数组里面添加
            ui->list->addItem(baseName);//向list控件里面添加基本名
        }
    }
}

void Editor::deleteItems()
{
    QList<QListWidgetItem*> removelist=ui->list->selectedItems();

    QListWidgetItem* temp;
    for(int i=0;i<removelist.size();++i){
        for(int j=i;j<removelist.size()-1;++j){
            if((ui->list->row(removelist[j]))>(ui->list->row(removelist[j+1]))){
                temp=removelist[j+1];
                removelist[j+1]=removelist[j];
                removelist[j]=temp;
            }
        }
    }//默认顺序是按点击顺序，这里用冒泡排序重新按index排序，防止段错误

    for(int j=removelist.size()-1;j>=0;j--){
        //我始终觉着QStringList还是封装STL的结果
        int id=ui->list->row(removelist[j]);
        QString name=list[id];
        QFileInfo info(name);
        QDir dir; dir.setPath(QString(WAREHOUSEPATH)+info.baseName()); dir.removeRecursively();
        list.erase(list.begin()+id);
        //在list数组中删除，倒序（避免segment error）
    }
    for(int j=0;j<removelist.size();++j){
        ui->list->removeItemWidget(removelist[j]);
        delete removelist[j];
        //在list控件中删除

        /*why delete?
         * 说实话，new，delete运算符配套使用是个好习惯，但是qt有所简化，利用对象树会自动释放。
         * 但是这里不要delete的话不会自动重绘
         * 故，要么delete，要么update
        */
    }
}

void Editor::renew()
{
    //注意，我们从未在editor界面操作时调用过renew(主要用于进入eidtor的初始化)
    ui->list->clear();//清空list控件的items
    list.clear();//清空list（QStringList）数组，便于append新对象

    readList();//读取ini_file,并添加item到list数组和list控件中

    quickIndex=-1;//主要用于进入eidtor的初始化
    quickShow();//展示图片
}

void Editor::readList()
{
    inifile->open(QIODevice::ReadOnly);//只读打开

    QString row;
    while(!inifile->atEnd()){
        //未到文件尾部，就是！=EOF或者~scanf()
        //readline
        row=inifile->readLine();
        //去除两头blank字符
        row=row.trimmed();
        list.append(row);
        //向list数组
        QFileInfo info(row);
        ui->list->addItem(info.baseName());
        //list控件
    }
    inifile->close();
}

void Editor::quickShow()
{
    ui->label->setScaledContents(true);
    if(list.size()==0){
        this->ui->label->setText("NULL");
        //如果没有图片，editor的展示就显示NULL；
        //已经在ui的stylesheet设置居中
    }
    else{
        //至少存在一张
        Widget* ptr=static_cast<Widget*>(this->parent());
        if(quickIndex>=0&&quickIndex<list.size()){
                //如果quickIndex合法，就不再改变
                ui->label->setPixmap(list[quickIndex]);
        }
        else if(ptr->previewIndex>=0&&ptr->previewIndex<list.size()){
                //前提是quickIndex完全失效
                //如果预览的图片合法，则默认显示预览图，并更新
                quickIndex=ptr->previewIndex;
                ui->label->setPixmap(list[quickIndex]);
        }
        else{
            //否则展示第一张，并更新
            ui->label->setPixmap(list[0]);
            quickIndex=0;
        }
    }
}
void Editor::renewList()
{
    inifile->open(QIODevice::WriteOnly);//只写打开
    for(QStringList::iterator i=list.begin();i!=list.end();++i){
        inifile->write(i->toUtf8().data());//QString转换为c_str
        inifile->write("\r\n");//换行
    }
    inifile->close();
}
void Editor::closeEvent(QCloseEvent *event)
{
    emit signalChangePic();//刷新图片
    return QWidget::closeEvent(event);
}
