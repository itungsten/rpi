#ifndef TRANSFORMER_H
#define TRANSFORMER_H
#include<QString>
#include<QFileInfo>

class Transformer
{
public:
    Transformer();
    void transform(QString path);

    QFileInfo info;
};

#endif // TRANSFORMER_H
