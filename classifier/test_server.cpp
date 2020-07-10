#include<iostream>
#include<fstream>
#include<string>
#include<sys/stat.h>
#include<spawn.h>
#include<unistd.h>
#include<sys/types.h>
#include<fcntl.h>
#define FIFOPATH "/tmp/magicAlbumFIFO"
using namespace std;

int main(int argc, char *argv[]) {
    mknod(FIFOPATH, S_IFIFO | 0666, 0);
    int child_pid;
    char * arg[]={"/usr/bin/python","client.py",NULL};
    char * env[]={"LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1",NULL};
    posix_spawn(&child_pid,"/usr/bin/python",nullptr,nullptr,arg,env);
    ifstream f(FIFOPATH);
    string line;
    while(1){
        getline(f,line);
        int val= stoi(line);
        if (!f.good()) {
            cerr << "Read failed" << endl;
        }
        else cout<<val<<endl;
        sleep(1);
        }
}
