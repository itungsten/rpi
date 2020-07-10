#ifndef TRANSFORMER_H
#define TRANSFORMER_H
#include<QString>
#include<QDir>
#include<QFileInfo>

class Transformer
{
public:
    Transformer();
    int classifier();
    void transform(QString path);

    QDir dir;
    QFileInfo info;
};

#endif // TRANSFORMER_H
