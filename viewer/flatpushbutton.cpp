#include "flatpushbutton.h"
#include "ui_flatpushbutton.h"
#include<QWidget>
#include<QPushButton>
#include"conf.h"

FlatPushButton::FlatPushButton(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::FlatPushButton)
{
    ui->setupUi(this);
    setStyleSheet("QPushButton:hover{background-color:rgb(215,215,215)}"
                  "QPushButton:pressed{background-color:rgb(195,195,195)}"
                  "QPushButton:focus{outline:none;}");
    //设置hover和press的背景色 取消焦点虚线框
}

FlatPushButton::~FlatPushButton()
{
    delete ui;
}
