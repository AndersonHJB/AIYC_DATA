# -*- coding: utf-8 -*-
import datetime
from cmath import inf
import requests
import re
import os
import urllib.request
import sys
from bs4 import BeautifulSoup
import time
import json
import configparser
import subprocess
import logging
import threading
import platform

version = 211212  # 请注意把下面这个地方和文件名改了就行啦
# pyinstaller -F 抖音直播录制_211212.py


class Logger(object):
    def __init__(self, stream=sys.stdout):
        output_dir = "log"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        log_name = "崩溃记录日志.log"
        filename = os.path.join(output_dir, log_name)
        self.terminal = stream
        self.log = open(filename, 'w', encoding="utf-8-sig")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


sys.stdout = Logger(sys.stdout)  # 将输出记录到log
sys.stderr = Logger(sys.stderr)  # 将错误信息记录到log
# 创建一个logger
logger = logging.getLogger('抖音直播录制%s版' % str(version))
logger.setLevel(logging.INFO)
# 创建一个handler，用于写入日志文件
if not os.path.exists("log"):
    os.makedirs("log")
fh = logging.FileHandler("log/直播日志文件.log", encoding="utf-8-sig", mode="a")
fh.setLevel(logging.WARNING)
# 再创建一个handler，用于输出到控制台
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# formatter = logging.Formatter()
# ch.setFormatter(formatter)
# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
# ch.setFormatter(formatter)
# 给logger添加handler
logger.addHandler(fh)
# logger.addHandler(ch)
# socket.setdefaulttimeout(10)


recording = []
unrecording = []

logger.warning("------------------------------------------------------")  # 分割线


def updateFile(file, old_str, new_str):
    file_data = ""
    with open(file, "r", encoding="utf-8-sig") as f:
        for line in f:
            if old_str in line:
                line = line.replace(old_str, new_str)
            file_data += line
    with open(file, "w", encoding="utf-8-sig") as f:
        f.write(file_data)


def subwords(words):
    words = re.sub('[? * : " < >  / |]', '', words)
    words = re.sub(r'\\', '', words)
    return words


def get_roomid_by_api(rid):
    '''
    https://webcast.amemv.com/douyin/webcast/reflow/7062184392986348301?u_code=142e3e8ik&did=MS4wLjABAAAAiCjoTZGteGtIA6HFNoWHFS-XqOi2g0nmt3VDED73S8g&iid=MS4wLjABAAAADnsHRt_FL0j7PS5DWQHAHOqE6q3UyXkN4aRl4vg5nixBSEyI-Bmw3fZbgYnVhRWw&with_sec_did=1&ecom_share_track_params=%7B%22is_ec_shopping%22%3A%221%22%7D&utm_source=copy&utm_campaign=client_share&utm_medium=android&app=aweme
    '''
    if len(proxies2) > 0:
        res = requests.get(rid, headers=headers, proxies=proxies2, timeout=15)
    else:
        res = requests.get(rid, headers=headers, timeout=15)
    mobile_url = res.url
    matchObj = re.search(r"webcast\/reflow\/(\d+)", mobile_url, re.M | re.I)
    if matchObj == None:
        print("没有匹配到room_id"+mobile_url)
        return ""
    return matchObj.group(1)


def get_room_base_info(room_id):
    '''
    获取直播间基础信息
    '''
    room_url = 'https://webcast.amemv.com/webcast/room/reflow/info/?type_id=0&live_id=1&app_id=1128&room_id={}'.format(
        room_id)
    Modelheaders = {
        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 8.1.0; en-US; Nexus 6P Build/OPM7.181205.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.11.1.1197 Mobile Safari/537.36'
    }

    if len(proxies2) > 0:
        res = requests.get(room_url, headers=Modelheaders,
                           proxies=proxies2, timeout=15)
    else:
        res = requests.get(room_url, headers=Modelheaders, timeout=15)

    resp = res.json()
    return resp


def get_real_url(rid, startname, changestaute):
    global recording
    changestautenow = False
    room_id = get_roomid_by_api(rid)
    room_base_info = get_room_base_info(room_id)

    try:
        # 抖音状态码参考:
        room_status = str(room_base_info['data']['room']['status'])

        if room_status == "2":
            changestaute = room_status
            changestautenow = True
            logger.warning("直播间正在直播")
        elif room_status == "4":
            changestaute = room_status
            logger.warning("直播间直播已结束,正在等待下次开播")
        elif room_status == "1":
            changestaute = room_status
            logger.warning("直播间未直播")
        else:
            changestaute = room_status
            logger.warning("未知状态.直播间状态返回码: "+room_status)

        nowdate = time.strftime("%H:%M:%S", time.localtime())
        if changestaute != changestautenow:
            changestaute = changestautenow
            if changestautenow == True:
                logger.warning(startname+" 正在直播中 ")
                print("\r"+startname+" 正在直播 " + nowdate)
                if startname in unrecording:
                    unrecording.append(startname)
            else:

                logger.warning(startname+"  直播间未直播,等待开播中.. ")
                #print(startname+"  直播间未直播,等待开播中.. "+nowdate)
                if startname in recording:
                    recording.remove(startname)
                if startname not in unrecording:
                    unrecording.append(startname)

        else:
            if changestautenow == True:
                print("\r"+startname+" 正在直播中 " + nowdate)
            else:
                #print(startname+"  直播间未直播,等待开播中.. "+nowdate)
                if startname in recording:
                    recording.remove(startname)
                if startname not in unrecording:
                    unrecording.append(startname)

        hls_pull_url = room_base_info['data']['room']['stream_url']['hls_pull_url']
        if videom3u8:
            print(startname + " 在线直播地址:" + str(hls_pull_url))

        real_url = room_base_info['data']['room']['stream_url']['rtmp_pull_url']
        return real_url, changestaute
    except Exception as _e:
        real_url = None
        return real_url, changestaute


headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 8.1.0; en-US; Nexus 6P Build/OPM7.181205.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.11.1.1197 Mobile Safari/537.36'
}

print('-------------- 程序当前配置----------------')
print("循环值守录制抖音直播 版本:%s" % str(version))

try:
    f = open("config.ini", 'r', encoding='utf-8-sig')
    f.close()

except IOError:
    f = open("config.ini", 'w', encoding='utf-8-sig')
    f.close()


try:
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8-sig')
    rid = config.get('1', '直播地址')
except:
    rid = ""


if os.path.isfile("URL_config.ini"):
    f = open("URL_config.ini", 'r', encoding='utf-8-sig')
    inicontent = f.read()
    f.close()
else:
    inicontent = ""


if len(inicontent) == 0:
    print('请输入要录制的抖音主播分享网址,例如: https://v.douyin.com/Lpy5rLT/:')
    inurl = input()
    f = open("URL_config.ini", 'a+', encoding='utf-8-sig')
    f.write(inurl)
    f.close()

    config = configparser.ConfigParser()

    config.read('config.ini', encoding='utf-8-sig')
    listx = []
    listx = config.sections()  # 获取到配置文件中所有分组名称
    if '1' not in listx:  # 如果分组type不存在则插入type分组
        config.add_section('1')

    else:
        config.remove_option('1', '直播地址')  # 删除type分组的stuno
        # config.remove_section('tpye')# 删除配置文件中type分组

    # config.set('1', '直播地址', inurl)# 给type分组设置值
    config.set('1', '循环时间(秒)', '60')  # 给type分组设置值

    o = open('config.ini', 'w', encoding='utf-8-sig')

    config.write(o)

    o.close()  # 不要忘记关闭


try:
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8-sig')
    delaydefault = config.getint('1', '循环时间(秒)')
except:
    config = configparser.ConfigParser()
    # -read读取ini文件
    config.read('config.ini', encoding='utf-8-sig')
    listx = []
    listx = config.sections()  # 获取到配置文件中所有分组名称
    if '1' not in listx:  # 如果分组type不存在则插入type分组
        config.add_section('1')

    else:
        config.remove_option('1', '循环时间(秒)')  # 删除type分组的stuno
        # config.remove_section('tpye')# 删除配置文件中type分组

    config.set('1', '循环时间(秒)', '60')  # 给type分组设置值

    o = open('config.ini', 'w', encoding='utf-8-sig')

    config.write(o)

    o.close()  # 不要忘记关闭
    delaydefault = 4


try:
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8-sig')
    videopath = config.get('1', '直播保存路径')
except:
    config = configparser.ConfigParser()
    # -read读取ini文件
    config.read('config.ini', encoding='utf-8-sig')
    listx = []
    listx = config.sections()  # 获取到配置文件中所有分组名称
    if '1' not in listx:  # 如果分组type不存在则插入type分组
        config.add_section('1')
    else:
        config.remove_option('1', '直播保存路径')  # 删除type分组的stuno
        # config.remove_section('tpye')# 删除配置文件中type分组

    config.set('1', '直播保存路径', '')  # 给type分组设置值

    o = open('config.ini', 'w', encoding='utf-8-sig')

    config.write(o)

    o.close()  # 不要忘记关闭
    videopath = ""

if len(videopath) > 0:
    if not os.path.exists(videopath):
        print("配置文件里,直播保存路径并不存在,请重新输入一个正确的路径.或留空表示当前目录,按回车退出")
        input("程序结束")
        os._exit(0)
    else:
        print("视频保存路径: "+videopath)
else:
    print("视频保存路径: 当前目录")


try:
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8-sig')
    videosavetype = config.get('1', '视频保存格式TS|FLV|MP4|MP3')

except Exception as _e:

    config = configparser.ConfigParser()
    # -read读取ini文件
    config.read('config.ini', encoding='utf-8-sig')
    listx = []
    listx = config.sections()  # 获取到配置文件中所有分组名称
    if '1' not in listx:  # 如果分组type不存在则插入type分组
        config.add_section('1')

    else:
        config.remove_option('1', '视频保存格式TS|FLV|MP4|MP3')  # 删除type分组的stuno
        # config.remove_section('tpye')# 删除配置文件中type分组

    config.set('1', '视频保存格式TS|FLV|MP4|MP3', "TS")  # 给type分组设置值

    o = open('config.ini', 'w', encoding='utf-8-sig')

    config.write(o)

    o.close()  # 不要忘记关闭
    videosavetype = "TS"


# 是否显示直播地址
try:
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8-sig')
    videom3u8 = config.get('1', '是否显示直播地址')

except Exception as _e:

    config = configparser.ConfigParser()
    # -read读取ini文件
    config.read('config.ini', encoding='utf-8-sig')
    listx = []
    listx = config.sections()  # 获取到配置文件中所有分组名称
    if '1' not in listx:  # 如果分组type不存在则插入type分组
        config.add_section('1')

    else:
        config.remove_option('1', '是否显示直播地址')  # 删除type分组的stuno
        # config.remove_section('tpye')# 删除配置文件中type分组

    config.set('1', '是否显示直播地址', "否")  # 给type分组设置值

    o = open('config.ini', 'w', encoding='utf-8-sig')

    config.write(o)

    o.close()  # 不要忘记关闭
    videom3u8 = "否"


if videom3u8 == "是":
    videom3u8 = True
else:
    videom3u8 = False


# 是否显示循环秒数
try:
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8-sig')
    looptime = config.get('1', '是否显示循环秒数')

except Exception as _e:

    config = configparser.ConfigParser()
    # -read读取ini文件
    config.read('config.ini', encoding='utf-8-sig')
    listx = []
    listx = config.sections()  # 获取到配置文件中所有分组名称
    if '1' not in listx:  # 如果分组type不存在则插入type分组
        config.add_section('1')

    else:
        config.remove_option('1', '是否显示循环秒数')  # 删除type分组的stuno
        # config.remove_section('tpye')# 删除配置文件中type分组

    config.set('1', '是否显示循环秒数', "否")  # 给type分组设置值

    o = open('config.ini', 'w', encoding='utf-8-sig')

    config.write(o)

    o.close()  # 不要忘记关闭
    looptime = "否"


if looptime == "是":
    looptime = True
else:
    looptime = False


# 这里是控制MP4是否转码
try:
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8-sig')
    videoencode = config.get('1', 'MP4格式是否转码H264')

except Exception as _e:

    config = configparser.ConfigParser()
    # -read读取ini文件
    config.read('config.ini', encoding='utf-8-sig')
    listx = []
    listx = config.sections()  # 获取到配置文件中所有分组名称
    if '1' not in listx:  # 如果分组type不存在则插入type分组
        config.add_section('1')

    else:
        config.remove_option('1', 'MP4格式是否转码H264')  # 删除type分组的stuno
        # config.remove_section('tpye')# 删除配置文件中type分组

    config.set('1', 'MP4格式是否转码H264', "否")  # 给type分组设置值

    o = open('config.ini', 'w', encoding='utf-8-sig')

    config.write(o)

    o.close()  # 不要忘记关闭
    videoencode = "否"


if videoencode == "是":
    videoencode = True
else:
    videoencode = False


# 这里是控制是否设置代理
try:
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8-sig')
    proxies2 = config.get('1', '本地代理端口')
    proxiesn = proxies2
    if len(proxies2) > 0:

        proxies2 = {'https': 'http://127.0.0.1:'+str(proxies2)}
        print("检测到有设置代理地址为: "+'http://127.0.0.1:'+str(proxiesn))

except Exception as _e:

    config = configparser.ConfigParser()
    # -read读取ini文件
    config.read('config.ini', encoding='utf-8-sig')
    listx = []
    listx = config.sections()  # 获取到配置文件中所有分组名称
    if '1' not in listx:  # 如果分组type不存在则插入type分组
        config.add_section('1')

    else:
        config.remove_option('1', '本地代理端口')  # 删除type分组的stuno
        # config.remove_section('tpye')# 删除配置文件中type分组

    config.set('1', '本地代理端口', "")  # 给type分组设置值

    o = open('config.ini', 'w', encoding='utf-8-sig')

    config.write(o)

    o.close()  # 不要忘记关闭

    proxies2 = ""


# 这里是控制TS是否分段
try:
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8-sig')
    Splitvideobysize = config.get('1', 'TS格式分段录制是否开启')


except Exception as _e:

    config = configparser.ConfigParser()
    # -read读取ini文件
    config.read('config.ini', encoding='utf-8-sig')
    listx = []
    listx = config.sections()  # 获取到配置文件中所有分组名称
    if '1' not in listx:  # 如果分组type不存在则插入type分组
        config.add_section('1')

    else:
        config.remove_option('1', 'TS格式分段录制是否开启')  # 删除type分组的stuno
        # config.remove_section('tpye')# 删除配置文件中type分组

    config.set('1', 'TS格式分段录制是否开启', "否")  # 给type分组设置值

    o = open('config.ini', 'w', encoding='utf-8-sig')

    config.write(o)

    o.close()  # 不要忘记关闭
    Splitvideobysize = "否"


if Splitvideobysize == "是":
    Splitvideobysize = True
else:
    Splitvideobysize = False


# 这里是控制TS分段大小

try:
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8-sig')
    Splitsize = config.getint('1', '视频分段大小(兆)')
except:
    config = configparser.ConfigParser()
    # -read读取ini文件
    config.read('config.ini', encoding='utf-8-sig')
    listx = []
    listx = config.sections()  # 获取到配置文件中所有分组名称
    if '1' not in listx:  # 如果分组type不存在则插入type分组
        config.add_section('1')
    else:
        config.remove_option('1', '视频分段大小(兆)')  # 删除type分组的stuno
        # config.remove_section('tpye')# 删除配置文件中type分组
    config.set('1', '视频分段大小(兆)', '1000')  # 给type分组设置值
    o = open('config.ini', 'w', encoding='utf-8-sig')
    config.write(o)
    o.close()  # 不要忘记关闭
    Splitsize = 1000  # 1g

# 分段大小不能小于5m
if Splitsize < 5:
    Splitsize = 5  # 最低不能小于5m

Splitsizes = Splitsize*1024*1024  # 分割视频大小,转换为字节


if Splitvideobysize:
    print("TS录制分段开启，录制分段大小为 %d M" % Splitsize)


if len(videosavetype) > 0:
    if videosavetype.upper() == "FLV":
        videosavetype = "FLV"
        print("直播视频保存为FLV格式")
    elif videosavetype.upper() == "TS":
        videosavetype = "TS"
        print("直播视频保存为TS格式")
    elif videosavetype.upper() == "MP4":
        videosavetype = "MP4"
        print("直播视频保存为MP4格式")
    elif videosavetype.upper() == "MP3":
        videosavetype = "MP3"
        print("直播视频保存为MP3音频格式")

    else:
        videosavetype = "TS"
        print("直播视频保存格式设置有问题,这次录制重置为默认的TS格式")
else:
    videosavetype = "TS"
    print("直播视频保存为TS格式")

if videoencode == True and videosavetype == "MP4":
    print("转码设置:MP4实时转码H264")

if videoencode == False and videosavetype == "MP4":
    print("转码设置:MP4不进行转码")


allLive = []  # 全部的直播
allRecordingUrl = []
print('......................................................')


def startgo(line):
    global allLive
    recordfinish = False
    recordfinish_2 = False
    counttime = time.time()
    global videopath

    ridcontent = line.split(',')
    rid = ridcontent[0]

    if len(ridcontent) > 1:
        print("传入地址: "+ridcontent[0], ridcontent[1])
    else:
        print("传入地址: "+ridcontent[0])

    while True:

        try:
            if len(proxies2) > 0:
                res = requests.get(rid, headers=headers,
                                   proxies=proxies2, timeout=15)
            else:
                res = requests.get(rid, headers=headers, timeout=15)

            if res.status_code != 200:
                print(res.status_code)
                # input('直播地址连接失败,请手动检测配置文件里的地址是否正常')
                print(rid+' 的直播地址连接失败,请手动检测配置文件里的地址是否正常')
            else:
                room_id = get_roomid_by_api(rid)
                resp = get_room_base_info(room_id)
                startname = resp['data']['room']['owner']['nickname']
                startname = subwords(startname)
                if startname in allLive:
                    print("新增的地址: %s 已经存在,本条线程将会退出" % startname)

                    namelist.append(str(rid)+"|"+str("#"+rid))
                    exit(0)

                if len(ridcontent) == 1:
                    namelist.append(
                        str(ridcontent[0])+"|"+str(ridcontent[0]+",主播: "+startname.strip()))

                break

        except Exception as e:
            print("错误信息644:"+str(e)+"\r\n读取的地址为: "+str(rid) +
                  " 发生错误的行数: "+str(e.__traceback__.tb_lineno))
            print(rid+' 的直播地址连接失败,请检测这个地址是否正常,可以重启本程序--requests获取失败')

        x = delaydefault
        if recordfinish == True:
            counttimeend = time.time()-counttime
            if counttimeend < 60:
                x = 2
            else:
                recordfinish = False
        else:
            x = delaydefault

        while x:
            x = x-1
            if looptime:
                print('\r循环等待%d秒 ' % x, end="")
            time.sleep(1)
        if looptime:
            print('\r重新检测直播间中...', end="")

    changestaute = ""
    while True:
        real_url, changestaute = get_real_url(rid, startname, changestaute)
        if changestaute==True and real_url != None:
            now = time.strftime("%Y-%m-%d-%H-%M-%S",
                                time.localtime(time.time()))
            try:
                if len(videopath) > 0:
                    if videopath[-1] != "/":
                        videopath = videopath+"/"
                    if not os.path.exists(videopath+startname):
                        os.makedirs(videopath+startname)
                else:
                    if not os.path.exists(startname):
                        os.makedirs('./'+startname)

            except Exception as e:
                print("路径错误信息708: "+str(e) + " 发生错误的行数: " +
                      str(e.__traceback__.tb_lineno))

            if not os.path.exists(videopath+startname):
                print("保存路径不存在,不能生成录制.请避免把本程序放在c盘,桌面,下载文件夹,qq默认传输目录.请重新检查设置")
                videopath = ""
                print("因为配置文件的路径错误,本次录制在程序目录")

            if videosavetype == "FLV":
                filename = startname + '_' + now + '.flv'
                if len(videopath) == 0:
                    print("\r"+startname+" 录制视频中: "+os.getcwd() +
                          "/"+startname + '/' + filename)
                else:
                    print("\r"+startname+" 录制视频中: " +
                          videopath+startname + '/' + filename)

                if not os.path.exists(videopath+startname):
                    print(
                        "目录均不能生成文件,不能生成录制.请避免把本程序放在c盘,桌面,下载文件夹,qq默认传输目录.请重新检查设置,程序将会退出")
                    input("请按回车退出")
                    os._exit(0)
                # flv录制格式

                try:
                    recording.append(startname)
                    _filepath, _ = urllib.request.urlretrieve(
                        real_url, videopath+startname + '/' + filename)
                    recordfinish = True
                    recordfinish_2 = True
                    counttime = time.time()
                    if startname in recording:
                        recording.remove(startname)
                    if startname in unrecording:
                        unrecording.append(startname)

                except:
                    print('\r'+time.strftime('%Y-%m-%d %H:%M:%S  ') +
                          startname + ' 未开播')

            elif videosavetype == "MP4":
                filename = startname + '_' + now + ".mp4"
                if len(videopath) == 0:
                    print("\r"+startname + " 录制视频中: "+os.getcwd() +
                          "/"+startname + '/' + filename)
                else:
                    print("\r"+startname + " 录制视频中: " +
                          videopath+startname + '/' + filename)

                ffmpeg_path = "./ffmpeg"
                file = videopath+startname + '/' + filename
                try:
                    recording.append(startname)
                    if videoencode:
                        _output = subprocess.check_output([
                            ffmpeg_path, "-y",
                            "-v", "verbose",
                            "-timeout", "10000000",  # 10s
                            "-loglevel", "error",
                            "-hide_banner",
                            "-user_agent", headers["User-Agent"],
                            "-analyzeduration", "2147483647",
                            "-probesize", "2147483647",
                            "-i", real_url,
                            '-bufsize', '5000k',
                            "-map", "0",
                            "-sn", "-dn",
                            # "-f","mpegts",
                            # "-bsf:v","h264_mp4toannexb",
                            # "-c","copy",
                            "-c:v", "libx264",  # 后期可以用crf来控制大小
                            # "-c:v","copy",   #直接用copy的话体积特别大.
                            '-max_muxing_queue_size', '64',
                            "{path}".format(path=file),
                        ], stderr=subprocess.STDOUT)
                    else:
                        _output = subprocess.check_output([
                            ffmpeg_path, "-y",
                            "-v", "verbose",
                            "-timeout", "10000000",  # 10s
                            "-loglevel", "error",
                            "-hide_banner",
                            "-user_agent", headers["User-Agent"],
                            "-analyzeduration", "2147483647",
                            "-probesize", "2147483647",
                            "-i", real_url,
                            '-bufsize', '5000k',
                            "-map", "0",
                            "-sn", "-dn",
                            # "-f","mpegts",
                            # "-bsf:v","h264_mp4toannexb",
                            # "-c","copy",
                            # "-c:v","libx264",   #后期可以用crf来控制大小
                            "-c:v", "copy",  # 直接用copy的话体积特别大.
                            '-max_muxing_queue_size', '64',
                            "{path}".format(path=file),
                        ], stderr=subprocess.STDOUT)

                    recordfinish = True
                    recordfinish_2 = True
                    counttime = time.time()
                    if startname in recording:
                        recording.remove(startname)
                    if startname in unrecording:
                        unrecording.append(startname)
                except subprocess.CalledProcessError as exc:
                    # logging.warning(str(exc.output))
                    print(str(exc.output) + " 发生错误的行数: " +
                          str(exc.__traceback__.tb_lineno))

            elif videosavetype == "MP3":
                filename = startname + '_' + now + ".mp3"
                if len(videopath) == 0:
                    print("\r"+startname+" 录制音频中: "+os.getcwd() +
                          "/"+startname + '/' + filename)
                else:
                    print("\r"+startname+" 录制音频中: " +
                          videopath+startname + '/' + filename)

                ffmpeg_path = "./ffmpeg"
                file = videopath+startname + '/' + filename
                try:
                    recording.append(startname)
                    _output = subprocess.check_output([
                        ffmpeg_path, "-y",
                        "-timeout", "10000000",  # 10s
                        "-user_agent", headers["User-Agent"],
                        "-i", real_url,
                        "{path}".format(path=file),
                    ], stderr=subprocess.STDOUT)

                    recordfinish = True
                    recordfinish_2 = True
                    counttime = time.time()
                    if startname in recording:
                        recording.remove(startname)
                    if startname in unrecording:
                        unrecording.append(startname)
                except subprocess.CalledProcessError as exc:
                    # logging.warning(str(exc.output))
                    print(str(exc.output) + " 发生错误的行数: " +
                          str(exc.__traceback__.tb_lineno))

            else:

                if(Splitvideobysize):  # 这里默认是启用/不启用视频分割功能
                    while(True):
                        now = time.strftime(
                            "%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
                        filename = startname + '_' + now + ".ts"
                        if len(videopath) == 0:
                            print("\r"+startname+" 分段录制视频中: "+os.getcwd()+"/" +
                                  startname + '/' + filename + " 每录满: %d M 存一个视频" % Splitsize)
                        else:
                            print("\r"+startname+" 分段录制视频中: "+videopath+startname +
                                  '/' + filename + " 每录满: %d M 存一个视频" % Splitsize)

                        ffmpeg_path = "./ffmpeg"
                        file = videopath+startname + '/' + filename
                        try:

                            recording.append(startname)
                            _output = subprocess.check_output([
                                ffmpeg_path, "-y",
                                "-v", "verbose",
                                "-timeout", "10000000",  # 10s
                                "-loglevel", "error",
                                "-hide_banner",
                                "-user_agent", headers["User-Agent"],
                                "-analyzeduration", "2147483647",
                                "-probesize", "2147483647",
                                "-i", real_url,
                                '-bufsize', '5000k',
                                "-map", "0",
                                "-sn", "-dn",
                                "-f", "mpegts",
                                # "-bsf:v","h264_mp4toannexb",
                                # "-c","copy",
                                "-c:v", "copy",
                                '-max_muxing_queue_size', '64',
                                "-fs", str(Splitsizes),
                                "{path}".format(path=file),
                            ], stderr=subprocess.STDOUT)

                            recordfinish = True  # 这里表示正常录制成功一次
                            recordfinish_2 = True
                            counttime = time.time()  # 这个记录当前时间, 用于后面 1分钟内快速2秒循环 这个值不能放到后面
                            if startname in recording:
                                recording.remove(startname)
                            if startname in unrecording:
                                unrecording.append(startname)
                        except subprocess.CalledProcessError as exc:
                            # logging.warning(str(exc.output))
                            print(str(exc.output) + " 发生错误的行数: " +
                                  str(exc.__traceback__.tb_lineno))
                            break
                else:
                    filename = startname + '_' + now + ".ts"
                    if len(videopath) == 0:
                        print("\r"+startname+" 录制视频中: "+os.getcwd() +
                              "/"+startname + '/' + filename)
                    else:
                        print("\r"+startname+" 录制视频中: " +
                              videopath+startname + '/' + filename)

                    ffmpeg_path = "./ffmpeg"
                    file = videopath+startname + '/' + filename
                    try:
                        recording.append(startname)
                        _output = subprocess.check_output([
                            ffmpeg_path, "-y",
                            "-v", "verbose",
                            "-timeout", "10000000",  # 10s
                            "-loglevel", "error",
                            "-hide_banner",
                            "-user_agent", headers["User-Agent"],
                            "-analyzeduration", "2147483647",
                            "-probesize", "2147483647",
                            "-i", real_url,
                            '-bufsize', '5000k',
                            "-map", "0",
                            "-sn", "-dn",
                            "-f", "mpegts",
                            # "-bsf:v","h264_mp4toannexb",
                            # "-c","copy",
                            "-c:v", "copy",
                            '-max_muxing_queue_size', '64',
                            "{path}".format(path=file),
                        ], stderr=subprocess.STDOUT)

                        recordfinish = True
                        recordfinish_2 = True
                        counttime = time.time()
                        if startname in recording:
                            recording.remove(startname)
                        if startname in unrecording:
                            unrecording.append(startname)
                    except subprocess.CalledProcessError as exc:
                        # logging.warning(str(exc.output))
                        print(str(exc.output) + " 发生错误的行数: " +
                              str(exc.__traceback__.tb_lineno))

        else:
            print('直播间不存在或未开播：'+line)
            pass

        if recordfinish_2 == True:
            if startname in recording:
                recording.remove(startname)
            if startname in unrecording:
                unrecording.append(startname)
            print('\n'+startname+" " +
                  time.strftime('%Y-%m-%d %H:%M:%S  ') + '直播录制完成\n')
            logger.warning(startname+" "+"直播录制完成")
            recordfinish_2 = False

        if recordfinish == True:
            counttimeend = time.time()-counttime
            if counttimeend < 60:
                x = 20  # 现在改成默认20s
            else:
                recordfinish = False
        else:
            x = delaydefault

        while x:
            x = x-1
            #print('\r循环等待%d秒 '%x)
            if looptime:
                print('\r循环等待%d秒 ' % x, end="")
            time.sleep(1)
        if looptime:
            print('\r检测直播间中...', end="")


start5 = datetime.datetime.now()


def displayinfo():
    global start5
    time.sleep(10)
    while True:
        os.system("cls") if platform.system().lower(
        ) == 'windows' else os.system("clear")
        print("循环值守录制抖音直播 版本:%s" % str(version))

        if len(recording) == 0 and len(unrecording) == 0:
            time.sleep(10)
            nowdate = time.strftime("%H:%M:%S", time.localtime())
            print("\r没有正在录制的直播,请检查配置文件是否为空 "+nowdate, end="")
            print("")

            continue
        else:
            print("正则监控 %i 个直播" % (len(recording)+len(unrecording)))
            if len(recording) > 0:
                print("x"*60)
                NoRepeatrecording = list(set(recording))
                nowdate = time.strftime("%H:%M:%S", time.localtime())
                print("正在录制%i个直播: " % len(NoRepeatrecording)+nowdate)
                for x in NoRepeatrecording:
                    print(x+" 正在录制中")
                #print("%i个直播正在录制中: "%len(NoRepeatrecording)+nowdate)
                end = datetime.datetime.now()
                print('总共录制时间: ' + str(end - start5))
                print("x"*60)
            else:
                start5 = datetime.datetime.now()

            if len(unrecording) > 0:
                NounRepeatrecording = list(set(unrecording))
                for x in NounRepeatrecording:
                    #logger.warning(x+"  直播间未直播,等待开播中.. ")
                    print(x+" :等待直播中")
            print("x"*60)
            time.sleep(10)


t = threading.Thread(target=displayinfo, args=(), daemon=True)
t.start()
runingList = []
texturl = []
textNoRepeatUrl = []
createVar = locals()
zz = 0
namelist = []
while True:
    file = open("URL_config.ini", "r", encoding="utf-8-sig")
    for line in file:
        line = line.strip()
        if line.startswith("#"):
            continue
        c = line.split()
        if len(c) == 0:
            continue
        else:
            c = line.strip()

            c = c.split('#')
            if len(line) < 20:
                continue

            texturl.append(line)

            # print(c[0])
    while len(namelist):
        a = namelist.pop()
        replacewords = a.split('|')
        updateFile(r"URL_config.ini", replacewords[0], replacewords[1])
    # 格式化后查找不一样
    file.close()
    if len(texturl) > 0:
        textNoRepeatUrl = list(set(texturl))

    if len(textNoRepeatUrl) > 0:
        for i in textNoRepeatUrl:
            formatcontent = i.split(',')
            # formatcontent[0] #这个为分离出的地址
            if formatcontent[0] not in runingList:
                #print("新增链接: "+ formatcontent[0])
                zz = zz+1
                createVar['thread' +
                          str(zz)] = threading.Thread(target=startgo, args=(i,))
                createVar['thread' + str(zz)].setDaemon(True)
                createVar['thread' + str(zz)].start()
                runingList.append(formatcontent[0])
    texturl = []
    time.sleep(3)


# print('程式结束,请按任意键退出')
input()
