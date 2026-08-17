# `Shell`脚本报错

## `Syntax error: Bad for loop variable`

**问题现象**

​	如下`Shell`脚本在运行时报错。

```shell
$ cat test.sh
#!/bin/sh
for ((i=0; i<100; i++))
do
        ./run.sh
done

$ ./test.sh
./test.sh: 3: Syntax error: Bad for loop variable
```

**问题原因**

​	从`ubuntu 6.10`开始，`ubuntu`就将先前默认的`bash shell`更换成了`dash shell`，其表现为`/bin/sh`链接到了`/bin/dash`而不是传统的`/bin/bash`，如下所示。

```shell
$ ls -l /bin/sh
lrwxrwxrwx 1 root root 4 Jan 15  2025 /bin/sh -> dash
```

​	所以在使用`sh`执行检测的时候实际使用的是`dash`，而`dash`不支持这种`C`语言格式的`for`循环写法。

**解决方法**

1、将默认`shell`更改成`bash`（笔者未尝试过）

```shell
$ sudo dpkg-reconfigure dash
#在选项中选No
```

2、直接使用`bash`检测

```shell
$ bash -n test.sh
```

3、指定脚本使用`bash`

```bash
# 修改前
#!/bin/sh

# 修改后
#!/bin/bash
```

4、修改脚本中`for`循环格式

```bash
#修改前
for ((i=1; i<100; i++))

# 修改后
for a in (1...100)
```

