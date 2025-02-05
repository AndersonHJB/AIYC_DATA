# -*- coding: utf-8 -*-
# @Author: AI悦创
# @Date:   2021-09-15 22:15:30
# @Last Modified by:   aiyc
# @Last Modified time: 2021-09-15 23:21:44
import jieba
import wordcloud
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

# 输入参数为要分析的 html 文件名，返回值为对应的 BeautifulSoup 对象
def create_doc_from_filename(filename):
	with open(filename, "r", encoding='utf-8')as f:
		html_content = f.read()
	doc = BeautifulSoup(html_content, "lxml")
	return doc


def parse(doc):
	post_list = doc.find_all("div",class_="post-info")
	result = []
	for post in post_list:
		link = post.find_all("a")[1]
		result.append(link.text.strip())

	result_str="\n".join(result)
	with open("news_title.txt", "w", encoding='utf-8') as fo:
		fo.write(result_str)


def create_ciyun():
	text = ""
	with open ("news_title.txt", encoding="utf-8") as fo:
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

def main():
	filename = "tips1.html"
	doc = create_doc_from_filename(filename)
	parse(doc)
	create_ciyun()

if __name__ == '__main__':
	main()