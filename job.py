#!/usr/bin/env python3

import urllib.request
import urllib.parse
import re
import time
from weiboPy3 import APIClient
import sys

APP_KEY = '<your app key>'
APP_SECRET = '<your app secret>'
CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'
AUTH_URL = 'https://api.weibo.com/oauth2/authorize'
USERID = '<your mail address>'
PASSWD = '<your password>'


def getCode(client):
    refererUrl = client.get_authorize_url()
    postdata = {"client_id": APP_KEY,
                "redirect_uri": CALLBACK_URL,
                "userId": USERID,
                "passwd": PASSWD,
                "isLoginSina": "0",
                "action": "submit",
                "response_type": "code",
                }
    headers = {
        "Referer": refererUrl
    }
    req = urllib.request.Request(
        AUTH_URL, urllib.parse.urlencode(postdata).encode('utf8'), headers)
    res = urllib.request.urlopen(req)
    code = res.geturl()[-32:]
    return code


def sendMsg(msg):
    client = APIClient(APP_KEY, APP_SECRET, CALLBACK_URL)
    code = getCode(client)
    r = client.request_access_token(code)
    access_token = r.access_token
    expires_in = r.expires_in
    client.set_access_token(access_token, expires_in)
    client.post.statuses__update(status=msg)


def getTodayJob():
    url = 'http://job.ustc.edu.cn/list.php?MenuID=002001'
    req = urllib.request.urlopen(url)
    data = req.read().decode('gbk')

    rule = re.compile('<li>([\w\W]*?)</li>')
    rule2 = re.compile(
        '<a href="([\w\W]*?)".*?>([\w\W]*?)</a><span class="zhiwei">([\w\W]*?)</span><span class="zhuanye">([\w\W]*?)</span>')
    info = rule.findall(data)
    t = time.localtime()
    year = str(t.tm_year)
    if len(str(t.tm_mon)) < 2:
        month = '0' + str(t.tm_mon)
    else:
        month = str(t.tm_mon)
    if len(str(t.tm_mday)) < 2:
        day = '0' + str(t.tm_mday)
    else:
        day = str(t.tm_mday)
    today = '-'.join([year, month, day])
    todayInfo = []
    for i in info:
        if today in i:
            todayInfo.append(i)
    detail = []
    for i in todayInfo:
        detail.append(rule2.findall(i))

    res = map(lambda x: x[0], detail)
    return list(res)

if __name__ == '__main__':
    while True:
        try:
            t = time.localtime()
            if t.tm_hour == 6 and t.tm_min == 0:
                base = 'http://job.ustc.edu.cn/'
                jobs = getTodayJob()
                if len(jobs) > 0:
                    for i in jobs:
                        url = base + i[0]
                        corp = i[1].replace(' ', '')
                        when = i[2].replace(' ', '')
                        where = i[3].replace(' ', '')
                        msg = url + corp + when + where
                        sendMsg(msg)
                        time.sleep(60)
            time.sleep(50)
        except Exception:
            print(sys.exc_info())
