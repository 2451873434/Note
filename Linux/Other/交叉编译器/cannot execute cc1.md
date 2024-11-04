# `arm-none-linux-gnueabihf-gcc: fatal error: cannot execute ‘cc1’: execvp: No such file or directory`

## 问题现象

​	在使用交叉编译器编译内核时，出现如下错误：

```
arm-none-linux-gnueabihf-gcc: fatal error: cannot execute ‘cc1’: execvp: No such file or directory
compilation terminated.
```

## 问题原因

​	这是由于你将交叉编译器中`bin`目录下的所有文件直接全部放到`/usr/bin`目录下，导致系统能够识别到`arm-none-linux-guneabihf-gcc -v`指令，但是在使用交叉编译器时却会报缺少`cc1`文件。实际上该交叉编译器所需的`cc1`文件在该交叉编译器中`libexec/gcc/arm-none-linux-guneabihf/9.2.1`下。

​	另外提一下，系统默认使用的`gcc`编译器，其所使用的`cc1`文件在`/usr/lib/gcc/x86_64_linux-gnu/7.5.0/`目录下。

## 解决方法

​	所以在安装交叉编译器的时候，不能简单的拷贝所用的`bin`文件下的工具，而是应该按照正常流程安装，即添加`PATH`路径，如下：

```bash
$ vim /ect/profile
# 在该文件的最后一行添加下面一行代码
export PATH=$PATH:/usr/local/toolchains/gcc-arm-9.2-2019.12-x86_64-arm-none-linux-gnueabihf/bin

$ source /etc/profile
```

