# author: wrfeng
# contact: feng@forchange.tech
# datetime:2022/1/26 10:15 上午

"""
文件说明：

"""
import time

import requests
import re
import os


class DouYin:

    def __init__(self, rid):
        self.rid = rid

    def get_real_url(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, '
                          'like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        }
        try:
            if 'v.douyin.com' in self.rid:
                room_id = re.findall(r'(\d{19})', requests.get(url=self.rid).url)[0]
            else:
                room_id = self.rid
            room_url = 'https://webcast.amemv.com/webcast/room/reflow/info/?type_id=0&live_id=1&app_id=1128&room_id={}'.format(room_id)
            response = requests.get(url=room_url, headers=headers).text
            rtmp_pull_url = re.search(r'"flv_pull_url":{"FULL_HD1":"(.*?flv)"', response).group(1)
            
            hls_pull_url = re.search(r'"hls_pull_url":"(.*?m3u8)"', response).group(1)
            real_url = [rtmp_pull_url, hls_pull_url]
        except:
            raise Exception('直播间不存在或未开播或参数错误')
        return real_url

    def recording(self, real_url, video_file, audio_file=""):
        os.system("ffmpeg -y -i {} {} -f wav {}".format(real_url, video_file, audio_file))


if __name__ == '__main__':
    r = input('请输入抖音直播间room_id或分享链接：\n')
    dy = DouYin(r)
    url = dy.get_real_url()
    dy.recording(url[1], './test.ts', './test.wav')
