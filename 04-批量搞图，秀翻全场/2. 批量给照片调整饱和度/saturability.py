# -*- coding: utf-8 -*-
# @Author: AI悦创
# @Date:   2021-10-04 21:25:28
# @Last Modified by:   aiyc
# @Last Modified time: 2021-10-04 21:30:12
import cv2
import numpy as np
import os

def process_image(file_path, target_dir):
	pic = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
	pic1 = cv2.cvtColor(pic, cv2.COLOR_BGR2HSV)
	H,S,V = cv2.split(pic1)
	new_pic = cv2.merge([np.uint8(H ), np.uint8(S * 1.5), np.uint8(V)])
	pic2 = cv2.cvtColor(new_pic, cv2.COLOR_HSV2BGR)
	file_name = file_path.split("/")[-1]
	cv2.imwrite(os.path.join(target_dir, file_name), pic2)

root, dirs, files = next(os.walk("tips_3/"))
for item in files:
	file_path = os.path.join(root,item)
	process_image(file_path, "tips_3_sa")

def mkdirs(self):
		if not os.path.exists(self.output_dir):
			os.makedirs(self.output_dir)
			print(f"文件夹 {self.output_dir} 已经自动为你创建，图片将保存到：{self.output_dir}")
		else:
			print(f"文件夹 {self.output_dir} 已经存在，图片将保存到：{self.output_dir}")