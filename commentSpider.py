import os
import base64
import requests
import logging
import json
import http.cookiejar
import urllib.parse
from bs4 import BeautifulSoup
import time
import sys

sys.setrecursionlimit(100000)
import re
import random
from urllib import parse
IDENTIFY = 1  # 验证码输入方式:        1:看截图aa.png，手动输入     2:云打码
COOKIE_GETWAY = 0 # 0 代表从https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18) 获取cookie   # 1 代表从https://weibo.cn/login/获取Cookie
logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.WARNING)  # 将selenium的日志级别设成WARNING，太烦人
myWeiBo = [

]
def getCookie(account, password):
    if COOKIE_GETWAY == 0:
        return get_cookie_from_login_sina_com_cn(account, password)
    # elif COOKIE_GETWAY ==1:
    #     return get_cookie_from_weibo_cn(account, password)
    # else:
        logger.error("COOKIE_GETWAY Error!")
user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
headers = {'User-Agent': user_agent, 'Connection': 'close'}
def get_cookie_from_login_sina_com_cn(account, password):
    """ 获取一个账号的Cookie """
    loginURL = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)"
    username = base64.b64encode(account.encode("utf-8")).decode("utf-8")
    postData = {
        "entry": "sso",
        "gateway": "1",
        "from": "null",
        "savestate": "30",
        "useticket": "0",
        "pagerefer": "",
        "vsnf": "1",
        "su": username,
        "service": "sso",
        "sp": password,
        "sr": "1440*900",
        "encoding": "UTF-8",
        "cdult": "3",
        "domain": "sina.com.cn",
        "prelt": "0",
        "returntype": "TEXT",
    }
    session = requests.Session()
    r = session.post(loginURL, data=postData)
    jsonStr = r.content.decode("gbk")
    info = json.loads(jsonStr)
    if info["retcode"] == "0":
        logger.warning("Get Cookie Success!( Account:%s )" % account)
        cookie = session.cookies.get_dict()
        return cookie
        # return json.dumps(cookie)
    else:
        logger.warning("Failed!( Reason:%s )" % info["reason"])
        return ""
def getCookies(weibo):
    """ 获取Cookies """
    cookies = []
    for elem in weibo:
        account = elem['no']
        password = elem['psw']
        cookie  =  getCookie(account, password)
        if cookie != None:
            cookies.append(cookie)

    return cookies

def crawl(path,no,psw):
    dic = {}
    dic['no'] = no
    dic['psw'] = psw
    myWeiBo.append(dic)
    cookies = getCookies(myWeiBo)
    logger.warning("Get Cookies Finish!( Num:%d)" % len(cookies))
    cookie = requests.utils.cookiejar_from_dict(cookies[0])
    session = requests.session()
    session.cookies = cookie

    # 第一頁評論
    first_url = "https://weibo.com/aj/v6/comment/big?ajwvr=6&id=4319265517081260&from=singleWeiBo&__rnd="
    _rnd = time.time()

    _rnd = str(_rnd).split(".")[0]+str(_rnd).split(".")[1][:3]
    myhtml = session.get(first_url+_rnd,headers = headers).text

    # print(str(myhtml))
    next_page_re = re.compile(r'node-type=\\"comment_loading\\" action-data=\\\"(.+?)\\')
    next_page_comment_url_list = next_page_re.findall(str(myhtml))
    next_page_comment_url = next_page_comment_url_list[0]
    # soup = BeautifulSoup(myhtml,"lxml")
    # print(soup.prettify())
    root_url = "https://weibo.com/aj/v6/comment/big?ajwvr=6&"
    current_url = root_url+next_page_comment_url+"&from=singleWeiBo&__rnd="

    _rnd = time.time()
    _rnd = str(_rnd).split(".")[0]+str(_rnd).split(".")[1][:3]
    print(current_url + _rnd)
    myhtml = session.get(current_url + _rnd, headers=headers).content
    print(myhtml)

crawl("","13750859160","wda50832211314")
