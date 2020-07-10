#ifndef CONF_H
#define CONF_H

#define BUF_SIZE 256
// 定义管道名 , 如果是跨网络通信 , 则在圆点处指定服务器端程序所在的主机名

#define WAREHOUSEPATH "/home/pi/Desktop/magicAlbum/warehouse/"
#define PYTHONPATH "/usr/bin/python"
#define CLIENTPATH "/home/pi/Desktop/magicAlbum/classifier/client.py"
#define CONFPATH "imgs.ini"
#define CMDBASEPATH "/home/pi/Desktop/magicAlbum/transformer/main.py"

#define FIFOPATH "/tmp/magicAlbumFIFO"


#include<sys/wait.h>
#include<sys/types.h>
#include<fcntl.h>
#include<sys/stat.h>
#include<unistd.h>
#include<spawn.h>


#endif // CONF_H
