from config import send_mail
import time


def control():
    while 1:
        cmd = input("输入控制命令,提示RC  ")
        if cmd == "0":
            input("请按enter退出")
            break
        else:
            result = send_mail("xxxxxxx@139.com", cmd)
            if result["result"] == "ok":
                print("控制命令-发送成功")
            else:
                print("控制命令-发送失败")
        time.sleep(1)


if __name__ == "__main__":
    control()
