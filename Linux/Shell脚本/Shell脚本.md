# Shell脚本

## 判断上一个命令是否执行成功

​	shell中使用符号“`$?`”来显示上一条命令执行的返回值，如果为0则代表成功，反之则失败。结合`if-else`语句实现判断上一个命令是否执行成功。

```shell
if [ $? -eq 0]; then
	echo "succeed"
else
	echo "failed"
fi
```

## for循环

```shell
# 简单用法
for i in "file1" "file2" "file3"
for i in /home/*
for i in (1...10)
for i in $(ls /home/)
for ((i=1; i<j; i++))

# 遍历数组
io_sch=("none" "mq-deadline" "bfq")
for index in "${!io_sch[@]}"
```

