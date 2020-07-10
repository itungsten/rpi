#ifndef EDITOR_H
#define EDITOR_H

#include <QWidget>
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
    void renew();
    void readList();
    void addItems();
    void deleteItems();
    void closeEvent(QCloseEvent *event);
    void quickShow();
    void renewList();


    Ui::Editor *ui;
    QString target="";//全屏时和预览时当前显示的动画的路径
    QMovie* now;//全屏时和预览时当前显示的动画的指针（指针复用嘛）
    QStringList list;//list数组，存放管理中的图像地址
    QString background="white";//背景色，鸡肋功能
    QFile* inifile;//文件句柄的指针
    QString inipath=CONFPATH;//配置文件地址，太懒了，不想写interval的配置
    int quickIndex=-1;//quickShow的索引

    Transformer transformer;

signals:
    void signalChangePic();//退出editor时，叫你换张图片
};

#endif // EDITOR_H
