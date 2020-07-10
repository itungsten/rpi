#ifndef FULLSCREEN_H
#define FULLSCREEN_H
#include<QWidget>
#include<QMovie>
#include<QImage>
#include<QPainter>
#include<fstream>


namespace Ui {
class FullScreen;
}

class FullScreen : public QWidget
{
    Q_OBJECT

public:
    explicit FullScreen(QWidget *parent = nullptr);
    ~FullScreen();

    void keyReleaseEvent(QKeyEvent *event);//按下Esc和Q可以退出全屏界面(但是好像raspi没键盘)

    //IPC(inter process communication)
    bool openPipe();
    void closePipe();
    //named pipe

    QMovie* anime; //animation to show

    int child_pid=-1;   //pid is the id of process
    std::ifstream* f;   //file handle of named pipe

    int lastCode=-1;    //上一次接受到的消息内容

    Ui::FullScreen *ui;
};

#endif // FULLSCREEN_H
