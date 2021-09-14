# file_name: excel_crawler_requests.py
import requests
import pandas as pd
from requests.exceptions import RequestException


def download_content(url):
	try:
		response = requests.get(url)
		if response.status_code == 200:
			return response.text
		else:
			return "None"
	except RequestException as e:
		return e


def save_excel(filename):
	html_content = download_content("http://fx.cmbchina.com/Hq/")
	# 调用 read_html 函数，传入网页的内容，并将结果存储在 cmb_table_list 中
	# read_html 函数返回的是一个 DataFrame 的list
	cmb_table_list = pd.read_html(html_content)
	# 通过打印每个 list 元素，确认我们所需要的是第二个，也就是下标 1
	# print(cmb_table_list)
	cmb_table_list[1].to_excel(filename)


def main():
	filename = "tips2.xlsx"
	save_excel(filename)

if __name__ == '__main__':
	main()



