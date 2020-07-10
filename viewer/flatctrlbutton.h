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
    void mouseReleaseEvent(QMouseEvent *event);
    void enterEvent(QEvent *ev);
    void leaveEvent(QEvent *ev);
    explicit FlatCtrlButton(QWidget *parent = nullptr);
    //nullptr就是NULL，explicit防止隐式调用构造函数进行类型转换
    ~FlatCtrlButton();


    Ui::FlatCtrlButton *ui;


signals:
    void signalClicked();//信号娘：哎呦，我被戳了一下（daze
};

#endif // flatCTRLBUTTON_H
