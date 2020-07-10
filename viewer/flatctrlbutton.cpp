#include "flatctrlbutton.h"
#include "ui_flatctrlbutton.h"
#include<QMessageBox>
#include<QWidget>
#include"conf.h"

FlatCtrlButton::FlatCtrlButton(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::FlatCtrlButton)
{
    ui->setupUi(this);//利用ui文件，布局
    this->ui->pushBtn->setAttribute(Qt::WA_TransparentForMouseEvents);//设置鼠标穿透效果
    this->ui->pushBtn->setVisible(false);//默认不显示代表切换的方向键
}

FlatCtrlButton::~FlatCtrlButton()
{
    delete ui;
}


void FlatCtrlButton::mouseReleaseEvent(QMouseEvent *ev)
{
    emit signalClicked();//槽接受信号后，切换图片
    return QWidget::mouseReleaseEvent(ev);
}

void FlatCtrlButton::enterEvent(QEvent *ev)
{
    this->ui->pushBtn->setVisible(true);//可见
    return QWidget::enterEvent(ev);
}

void FlatCtrlButton::leaveEvent(QEvent *ev)
{
    this->ui->pushBtn->setVisible(false);//不可见
    return QWidget::leaveEvent(ev);
}
