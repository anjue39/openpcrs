import time
import requests

def download_speed_test(download_results, proxy, download_test_url, download_test_timeout, sema_download):
    """
    下载速度测试

    Args:
        download_results (list): 下载结果保存列表
        proxy (dict): 代理信息
        download_test_url (str): 下载测试文件的 URL
        download_test_timeout (int): 下载超时时间
        sema_download (multiprocessing.Semaphore): 控制并发下载的信号量
    """
    try:
        start_time = time.time()
        response = requests.get(download_test_url, proxies=proxy, timeout=download_test_timeout)
        end_time = time.time()
        total_time = end_time - start_time
        file_size = len(response.content)
        file_in_mb = file_size / (1024 * 1024)
        speed_in_mb = file_in_mb / (total_time - latency)
        proxy['speed'] = speed_in_mb
    except requests.exceptions.RequestException:
        proxy['speed'] = 0  # 请求异常，速度为 0

    download_results.append(proxy)
