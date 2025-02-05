# -*- coding: utf-8 -*-
# @Author: AI悦创
# @Date:   2021-10-02 10:26:52
# @Last Modified by:   aiyc
# @Last Modified time: 2021-10-04 21:11:59
import cv2
import numpy
from PIL import Image, ImageDraw, ImageFont
import os

class WaterMark(object):
	def __init__(self, OperationFilename=".", output_dir="watermark", textSize=10, watermarkText="水印", textColor="#ffffff", system=False, winfontfile=r"C:\Windows\Fonts\STZHONGS.ttf", macfontfile="/System/Library/Fonts/PingFang.ttc"):
		self.OperationFilename = OperationFilename
		self.output_dir = output_dir
		self.textSize = textSize
		self.watermarkText = watermarkText
		self.textColor = textColor
		self.system = system
		self.winfontfile = winfontfile
		self.macfontfile = macfontfile

	def mkdirs(self):
		if not os.path.exists(self.output_dir):
			os.makedirs(self.output_dir)
			print(f"文件夹 {self.output_dir} 已经自动为你创建，图片将保存到：{self.output_dir}")
		else:
			print(f"文件夹 {self.output_dir} 已经存在，图片将保存到：{self.output_dir}")



	def system_font(self):
		if not self.system:
			return ImageFont.truetype(self.textSize, encoding="utf-8")
		if self.system.upper() == "MAC":
			# FontFilePath = "/System/Library/Fonts/PingFang.ttc"
			return ImageFont.truetype(font=self.macfontfile, size=self.textSize, encoding="utf-8")
		elif self.system.upper() == "WINDOWS":
			# FontFilePath = r"C:\Windows\Fonts\STZHONGS.ttf"
			return ImageFont.truetype(font=self.winfontfile, size=self.textSize, encoding="utf-8")
	
	def parsepath(self):
		path_lst = []
		# a = os.walk("tips_3/")
		root, dirs, files = next(os.walk(self.OperationFilename))
		# root, dirs, files = next(os.walk("tips_3/"))
		# print(list(a))
		for item in files:
			file_path = os.path.join(root, item)
			# self.process_file(file_path)
			path_lst.append(file_path)
		return path_lst

	def process_file(self, file_path):
		img = cv2.imread(file_path)
		image_shape = img.shape
		height = image_shape[0]
		width = image_shape[1]
		# print(img.size)
		if (isinstance(img, numpy.ndarray)):
			img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
		draw = ImageDraw.Draw(img)
		fontStyle = self.system_font()
		# 绘制文本
		# textColor = (168, 121, 103)
		draw.text((width/2, height-30), self.watermarkText, self.textColor, font=fontStyle)
		# draw.text((width/2, height-30), self.watermarkText, fill=self.textColor, font=fontStyle)
		# 转换回 OpenCV 类型
		img2 = cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)
		# 保存图片
		file_name = file_path.split("/")[-1]
		cv2.imwrite(os.path.join(self.output_dir, file_name), img2)
		print(f"proceed {file_path}")

	def main(self):
		self.mkdirs()
		path_lst = self.parsepath()
		# print(path_lst)
		for path in path_lst:
			self.process_file(path)
	

if __name__ == '__main__':
	run = WaterMark(
		OperationFilename="tips_3/", 
		output_dir="image_watermark",
		textSize=10,
		watermarkText="@黄家宝|www.aiyc.top",
		textColor="gray",
		system="Windows",
		winfontfile="JiZiJingDianKaiTiJianFan-.ttf")
	run.main()

