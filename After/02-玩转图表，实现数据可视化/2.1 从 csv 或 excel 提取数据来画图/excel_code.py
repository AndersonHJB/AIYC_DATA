# -*- coding: utf-8 -*-
# @Author: AI悦创
# @Date:   2021-09-14 21:56:37
# @Last Modified by:   aiyc
# @Last Modified time: 2021-09-15 17:09:43
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 使用 pandas 读取 excel， csv 文件的话换成 pd.read_csv 即可
df = pd.read_excel("tips2.xlsx")

# 因为第一行是中文表头，所以我们先过滤掉
df = df[df.index>0]
sns.set()
figure2 = plt.figure(figsize = (10, 5))
figure2.add_subplot(1,1,1)

# 设置轴的属性
plt.xlabel("",fontsize = 14)
plt.ylabel("卖出价", fontsize = 14)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.title("外汇情况", fontsize=14)

# 设置字体的属性
# plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]
# plt.rcParams["font.family"] = 'sans-serif'
plt.rcParams["font.sans-serif"] = "SimHei"
plt.rcParams["axes.unicode_minus"] = False

category = df[0]
index_category = np.arange(len(category))

# 将卖出价 转换为数字
df[3] = pd.to_numeric(df[3])
plt.xticks(rotation = 90)
plt.bar(x=df[0], height=df[3].values, color=[1,0,1])
plt.show()



