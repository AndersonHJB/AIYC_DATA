# -*- coding: utf-8 -*-
# @Author: AI悦创
# @Date:   2021-09-16 09:16:11
# @Last Modified by:   aiyc
# @Last Modified time: 2021-09-17 23:03:27
import jieba, wordcloud
import matplotlib.pyplot as plt
def create_ciyun(filename):
	text = ""
	with open (filename, encoding="utf-8") as fo:
		text = fo.read()
	split_list = jieba.lcut(text)
	final_text = " ".join(split_list)

	stopwords= ["的", "是", "了"]
	# Windows 系统的 font_path 替换为'C:\Windows\Fonts\STZHONGS.ttf'
	wc = wordcloud.WordCloud(font_path = r"C:\Windows\Fonts\STZHONGS.TTF", width=1000, height=700, background_color="white",max_words=100,stopwords = stopwords)
	wc.generate(final_text)
	plt.imshow(wc)
	plt.axis("off")
	plt.show()

if __name__ == '__main__':
	filename = "关于博主-AI悦创.html"
	create_ciyun(filename)


