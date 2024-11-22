# `Linux`创建`sysfs`属性节点

> 参考链接：
>
> [Linux创建sysfs属性节点](https://blog.csdn.net/hinewcc/article/details/138801636)
>
> [Linux驱动开发头文件剖析（十）：<linux/kstrtox.h>](https://zhuanlan.zhihu.com/p/690363054)

## 1、简介

​	在`Linux`驱动调试时，常常需要添加属性文件，`sysfs`属性节点可以实现用户空间与硬件交互，如：设置`GPIO`管脚电平、控制驱动等功能。使用`DEVICE_ATTR`可以实现驱动在`/sys/`目录自动创建文件，我们只需要实现`xxx_show()`和`xxx_store()`函数即可，然后在应用层就能通过`cat`和`echo`命令来对创建出来的文件进行读写操作，实现交互。

## 2、`DEVICE_ATTR`

```c
/* 路径：include/linux/device.h */
#define DEVICE_ATTR(_name, _mode, _show, _store) \
	struct device_attribute dev_attr_##_name = __ATTR(_name, _mode, _show, _store)
 
struct device_attribute {
    struct attribute	attr;
    ssize_t (*show)(struct device *dev, struct device_attribute *attr,
                    char *buf);
    ssize_t (*store)(struct device *dev, struct device_attribute *attr,
                     const char *buf, size_t count);
};
 
/* 路径：include/linux/sysfs.h */
#define __ATTR(_name, _mode, _show, _store) {				\
	.attr = {.name = __stringify(_name),				\
		 .mode = VERIFY_OCTAL_PERMISSIONS(_mode) },		\
	.show	= _show,						\
	.store	= _store,						\
}
```

​	`_name`：将在`sysfs`中生成的文件名称

​	`_mode`：属性文件的权限

​	`_show`：`cat`该文件时，此函数被调用

​	`_store`：`echo`内容到该文件时，此函数被调用

​	除了`DEVICE_ATTR`宏之外，还有更方便使用的`DEVICE_ATTR_RO`、`DEVICE_ATTR_WO`、`DEVICE_ATTR_RW`等。这些宏都是用来定义一个`struct device_attribute`结构体，并对各成员初始化，还需要使用`sysfs_create_file()`或`sys_create_group()`将属性文件加入`sysfs`文件系统中。

## 3、示例

```c
ssize_t para_show(struct device *dev, struct device_attribute *attr, char *buf)
{
    return 0;
}

ssize_t para_store(struct device *dev, struct device_attribute *attr, const char *buf, size_t count)
{
    return 0;
}

static DEVICE_ATTR_RW(para);

/* 如果是多个文件，则在此结构体中按同样的方式添加即可 */
static struct attribute *para_attribute[] =
{
    &dev_attr_para.attr,
    NULL,
};
/* group的两种定义，任选一种 */
static struct attribute_group para_group =
{
    .attrs = para_attribute,
};
/* group的两种定义，任选一种 */
ATTRIBUTE_GROUPS(para);

/* 入口函数 */
static int __init led_init(void)
{
    /* ... */
    sysfs_create_group(&stMyled.device->kobj, &para_group);
	
    return 0;
}

/* 出口函数 */
static void __exit led_exit(void)
{

}
```

## 4、其它函数

​	由于`echo`内容到文件时，`xxx_store()`函数会被调用，而`echo`的内容都是字符串的形式，所以`xxx_store()`函数中就可能会用到一些处理字符串的函数。

### 4.1 `kstrtouint()`

```c
int kstrtouint(const char *s, unsigned int base, unsigned int *res)
```

​	`s`：输入字符串

​	`base`：10表示10进制，16表示16进制，0表示自动识别

​	`res`：存放转换后的整型值

​	返回值：没有错误时返回值为0

​	`kstrtouint()`函数会将字符串转换为整型。此外，还有一些相似函数如`kstrtol()`、`kstrtoul()`、`kstrtoint()`等。

### 4.2 `strsep()`

```c
char *strsep(char **stringp, const char *delim)
```

​	`stringp`：指向被分隔字符串的指针的指针

​	`delim`：分隔的字符

​	返回值：被分隔后的左边的字符串，同时会导致`stringp`的值发生改变（`stringp`会变成右边那一段字符串）

​	`strsep()`函数以`delim`参数作为分界符，将`stringp`参数所指的字符串分割开。如使用`strsep()`函数对`1999-12-14`进行分割，返回值为`1999`，分割后的`stringp`为`12-14`。