# awk命令

> 参考链接：[linux中awk命令(最全面秒懂)](https://www.cnblogs.com/My-IronMan/p/15721682.html)

## 1、awk命令介绍

​	`awk`是一种处理文本文件的语言，是一个强大的文本分析工具。`linux`中有三剑客——`awk`，`grep`，`sed`。

​	`grep`：过滤文本

​	`sed`：修改文本

​	`awk`：处理文本

## 2、awk的语法格式

```
awk [参数] [处理内容] [操作对象]
```

​	awk中的预定义变量如下：

```
$0	: 代表当前行（相当于匹配所有）
	awk -F: '{print $0, "---"}' /etc/passwd
	
$n	: 代表第n列
eg1:（以":"为分隔符）
	awk -F: '{print NF}' /etc/passwd
eg2:（默认空格为分隔符）
	awk '{print $NF}' /etc/passwd
	
	
NF	: 记录当前统计总字段数
eg1:（统计文件内每行内的行数）
	awk -F: '{print NF}' /etc/passwd
eg2:（统计文件内每行总字段，并打印每行统计行数）
	awk -F: '{print $NF}' /etc/passwd
	

```

