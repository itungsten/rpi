#ifndef CONF_H
#define CONF_H


#define WAREHOUSEPATH "/home/pi/Desktop/magicAlbum/warehouse/"
#define PYTHONPATH "/usr/bin/python"
#define CLIENTPATH "/home/pi/Desktop/magicAlbum/classifier/client.py"
#define CONFPATH "imgs.ini"
#define TRANSFORMPATH "/home/pi/Desktop/magicAlbum/transformer/main.py"
//related paths in absolute form

#define FIFOPATH "/tmp/magicAlbumFIFO"
// 定义管道名(named pipe)
#define BUF_SIZE 256
// the size of message buffer

#define BACKGROUND "white"

#include<sys/wait.h>
#include<sys/types.h>
#include<fcntl.h>
#include<sys/stat.h>
#include<unistd.h>
#include<spawn.h>
//headers in linux


#endif // CONF_H
