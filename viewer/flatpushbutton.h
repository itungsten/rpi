#ifndef flatPUSHBUTTON_H
#define flatPUSHBUTTON_H

#include <QWidget>
#include <QPushButton>

namespace Ui {
class FlatPushButton;
}

class FlatPushButton : public QWidget
{
    Q_OBJECT

public:
    explicit FlatPushButton(QWidget *parent = nullptr);
    ~FlatPushButton();

    Ui::FlatPushButton *ui;
};

#endif // flatPUSHBUTTON_H
