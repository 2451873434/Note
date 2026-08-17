# `bad interpreter: No such file or directory`

## 问题现象

​	我们常常将从网站上下载脚本或工具直接放到`Linux`系统下运行，这时就有可能出现如`bad interpreter: No such file or directory`的报错信息。

## 问题原因

​	`Linux`系统无法识别出`Windows`的`DOS`格式，此时只需要将文件格式转换成`unix`即可。

## 解决方法

​	1、使用`vim`编辑出错文件

​	2、使用`:set ff`指令查看当前文件格式（一般情况下为`DOS`）

​	3、使用`:set ff=unix`修改文件格式为`unix`

​	4、使用`:wq`保存退出