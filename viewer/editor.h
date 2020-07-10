#ifndef EDITOR_H
#define EDITOR_H

#include<QWidget>
#include<QFile>
#include<QStringList>
#include"transformer.h"
#include"conf.h"

namespace Ui {
class Editor;
}

class Editor : public QWidget
{
    Q_OBJECT

public:
    explicit Editor(QWidget *parent = nullptr);
    ~Editor();

    void load();//加载管理界面
    void readList();//work for load()
    void dumpList();//退出管理界面时，保存配置
    void addItems();//add op.
    void deleteItems();//delete op.

    void quickShow();//管理界面右侧的速览(not 预览)
    void closeEvent(QCloseEvent *event);


    Ui::Editor *ui;
    QString target="";//全屏时和预览时当前显示的动画的路径
    QMovie* now;//全屏时和预览时当前显示的动画的指针
    QStringList list;//list数组，存放管理中的图像地址
    QString background=BACKGROUND;//背景色
    QFile* inifile;//文件句柄的指针
    int quickIndex=-1;//quickShow的索引

    Transformer transformer;//文件在被加入管理后，交付给变换器预处理

signals:
    void signalChangePic();//退出editor时，换张图片
};

#endif // EDITOR_H
