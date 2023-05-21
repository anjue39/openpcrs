import time
import subprocess
from multiprocessing import Process, Manager, Semaphore
from check import check
from tqdm import tqdm
from init import init, clean
from clash import push, checkenv, checkuse

if __name__ == '__main__':
    with Manager() as manager:
        alive = manager.list()
        # 初始化配置
        http_port, api_port, threads, source, timeout, outfile, proxyconfig, apiurl, testurl, testurl1, config = init()
        clashname, operating_system = checkenv()
        checkuse(clashname[2::], operating_system)
        # 启动 Clash 进程
        clash = subprocess.Popen([clashname, '-f', './temp/working.yaml', '-d', '.'])
        processes = []
        sema = Semaphore(threads)
        time.sleep(5)  # 等待 Clash 进程启动

        # 第一轮测试，使用 testurl
        for i in tqdm(range(len(config['proxies'])), desc="Testing Round 1"):
            sema.acquire()
            p = Process(target=check, args=(alive, config['proxies'][i], apiurl, sema, timeout, testurl))
            p.start()
            processes.append(p)
        for p in processes:
            p.join()

        # 将第一轮测试的结果保存为初始结果
        initial_alive = list(alive)

        # 如果存在第二轮测试的 testurl1，进行第二轮测试
        if testurl1 and testurl1.strip():
            processes = []
            second_round_alive = manager.list()

            # 第二轮测试，使用 testurl1，基于第一轮测试的活跃代理
            for proxy in tqdm(initial_alive, desc="Testing Round 2"):
                sema.acquire()
                p = Process(target=check, args=(second_round_alive, proxy, apiurl, sema, timeout, testurl1))
                p.start()
                processes.append(p)
            for p in processes:
                p.join()

            # 将第二轮测试的结果作为最终结果
            alive = list(second_round_alive)
            print("第二次测试结果数量:", len(alive))
        else:
            # 没有第二轮测试时，将第一轮测试的结果作为最终结果
            alive = list(initial_alive)
            print("只进行了第一次测试，结果数量:", len(alive))

        # 将测试结果写入文件
        push(alive, outfile)
        # 清理进程和临时文件
        clean(clash)
