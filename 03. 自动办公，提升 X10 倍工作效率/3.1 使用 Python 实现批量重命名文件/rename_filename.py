# -*- coding: utf-8 -*-
# @Author: AI悦创
# @Date:   2021-09-24 10:52:01
# @Last Modified by:   aiyc
# @Last Modified time: 2021-09-24 18:58:42
import os

root, dirs, files = next(os.walk("tips_3/"))

idx = 0

for item in files:
	old_file_path = os.path.join(root,item)
	new_file_path = os.path.join(root, f"aiyc_{idx}.jpg")
	os.rename(old_file_path, new_file_path)
	idx = idx + 1

