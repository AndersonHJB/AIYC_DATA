# file_name: excel_crawler_urllib3.py
import urllib3
import pandas as pd

def download_content(url):
	# 创建一个 PoolManager 对象，命名为 http
	http = urllib3.PoolManager()
	# 调用 http 对象的 request 方法，第一个参数传一个字符串 "GET"
	# 第二个参数则是要下载的网址，也就是我们的 url 变量
	# request 方法会返回一个 HTTPResponse 类的对象，我们命名为 response
	response = http.request("GET", url)

	# 获取 response 对象的 data 属性，存储在变量 response_data 中
	response_data = response.data

	# 调用 response_data 对象的 decode 方法，获得网页的内容，存储在 html_content
	# 变量中
	html_content = response_data.decode()
	return html_content

def save_excel():
	html_content = download_content("http://fx.cmbchina.com/Hq/")
	# 调用 read_html 函数，传入网页的内容，并将结果存储在 cmb_table_list 中
	# read_html 函数返回的是一个 DataFrame 的list
	cmb_table_list = pd.read_html(html_content)
	# 通过打印每个 list 元素，确认我们所需要的是第二个，也就是下标 1
	cmb_table_list[1].to_excel("tips2.xlsx")

def main():
	save_excel()

if __name__ == '__main__':
	main()