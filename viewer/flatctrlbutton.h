#ifndef flatCTRLBUTTON_H
#define flatCTRLBUTTON_H

#include <QWidget>

namespace Ui {
class FlatCtrlButton;
}

class FlatCtrlButton : public QWidget
{
    Q_OBJECT
//有这个宏就可以使用信号槽机制
public:
    void mouseReleaseEvent(QMouseEvent *event); //similar to click
    void enterEvent(QEvent *ev); //appear
    void leaveEvent(QEvent *ev); //disappear
    explicit FlatCtrlButton(QWidget *parent = nullptr);
    //explicit防止隐式调用构造函数
    ~FlatCtrlButton();


    Ui::FlatCtrlButton *ui;


signals:
    void signalClicked();
};

#endif // flatCTRLBUTTON_H
