from .options import Options
from .solvers import create_solver

def test(num=6,infile=None,outfile=None,ausPath=None,tarAus=None):
    opt = Options().parse()
    opt.results=outfile
    opt.data_root=infile
    opt.ausPath=ausPath
    opt.tarAus=tarAus
    opt.interpolate_len=num-1
    # print(infile)
    # print(outfile)
    #引入配置文件，并在这里读入参数
    solver = create_solver(opt)
    solver.is_train=0
    #利用配置创建求解器
    solver.single_networks(solver.opt)
    # solver.single_networks(solver.opt)
    #运行求解器
def normal():
    opt = Options().parse()
    #引入配置文件，并在这里读入参数
    solver = create_solver(opt)
    #利用配置创建求解器
    solver.run_solver()
    #运行求解器

    print('[THE END]')
    #结束

if __name__ == '__main__':
    opt = Options().parse()
    #引入配置文件，并在这里读入参数
    solver = create_solver(opt)
    #利用配置创建求解器
    solver.run_solver()
    #运行求解器

    print('[THE END]')
    #结束