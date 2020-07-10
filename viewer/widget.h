#ifndef WIDGET_H
#define WIDGET_H

#include "editor.h"
#include "fullscreen.h"

#include <QWidget>
#include<QTimer>
#include<QListWidget>
#include<QListWidgetItem>
#include<QEvent>
#include<QMouseEvent>

QT_BEGIN_NAMESPACE
namespace Ui { class Widget; }
QT_END_NAMESPACE

class Widget : public QWidget
{
    Q_OBJECT

public:
    Widget(QWidget *parent = nullptr);
    ~Widget();

    void flushPic();//用于刷新预览界面图片
    void leftPic();//用于向左切换图片
    void rgtPic();//用于向右切换图片
    void setStatusBar();//更新状态栏
    QSize getFullSize();//获取全屏时缩放后图片的尺寸

    void mouseMoveEvent(QMouseEvent* ev);//配合mousePressEvent添加窗口移动功能
    void mousePressEvent(QMouseEvent* ev);

    Ui::Widget *ui;
    int interval=1*100; //全屏时进程间通信消息接收的间隔，单位是msec
    QTimer* timer;  //计时器
    int previewIndex=-1; //预览界面（主界面）显示的图片的索引
    QString version="alpah3.0"; //版本号
    Editor* editor;//管理界面的指针
    FullScreen* full;//全屏界面的指针
    QSize dis;//用于存储当前鼠标点击点与窗口左上角的距离，用于移动窗口
};


#endif // WIDGET_H
