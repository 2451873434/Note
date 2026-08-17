# '__printf(a, b)'

## 函数声明

​	最近，在看`mcp2515`设备驱动的时候，发现该驱动有其特有的打印函数`netdev_err()`、`netdev_printk()`、`netdev_warn()`等，查询其声明时，代码如下：

```
__printf(3, 4) __cold
void netdev_printk(const char *level, const struct net_device *dev,
		   const char *format, ...);
__printf(2, 3) __cold
void netdev_err(const struct net_device *dev, const char *format, ...);
__printf(2, 3) __cold
void netdev_warn(const struct net_device *dev, const char *format, ...);
```

> 注意：这里只是函数的声明，还需要有对应的函数定义才能正常使用该函数。

​	可以发现，其声明中都存在`__printf(a, b)`的关键字，该关键字的定义如下：

```
#define __printf(a, b)                  __attribute__((__format__(printf, a, b)))
```

​	`__attribute__((__format__(printf, a, b)))`属性可以给被声明的函数加上类似`printf`的特征，它可以使编译器检查函数声明和函数实际调用参数之间的格式化字符串是否匹配。`format`属性告诉编译器，按照`printf`标准`C`函数参数格式规则对该函数的参数进行检查。这在我们自己封装调试信息的接口时非常有用。

​	`format`的语法格式如下：

```c
__format__(archetype, string-index, first-to-check)
```

* `archetype`：指定是哪种风格
* `string-index`：指定传入函数的第几个参数是格式化字符串
* `first-to-check`：指定从函数的第几个参数开始按上述规则进行检查



## 函数定义

​	以上述`netdev_printk()`、`netdev_err()`等函数为例，其定义有两种形式，如下：

```c
// 第一种定义
void netdev_printk(const char *level, const struct net_device *dev,
		   const char *format, ...)
{
	struct va_format vaf;
	va_list args;

	va_start(args, format);

	vaf.fmt = format;
	vaf.va = &args;

	__netdev_printk(level, dev, &vaf);

	va_end(args);
}
EXPORT_SYMBOL(netdev_printk);
```

```c
// 第二种定义
#define define_netdev_printk_level(func, level)			\
void func(const struct net_device *dev, const char *fmt, ...)	\
{								\
	struct va_format vaf;					\
	va_list args;						\
								\
	va_start(args, fmt);					\
								\
	vaf.fmt = fmt;						\
	vaf.va = &args;						\
								\
	__netdev_printk(level, dev, &vaf);			\
								\
	va_end(args);						\
}								\
EXPORT_SYMBOL(func);

define_netdev_printk_level(netdev_err, KERN_ERR);
define_netdev_printk_level(netdev_warn, KERN_WARNING);
```

​	`va_start()`宏用于初始化一个`va_list`变量，以便在可变参数函数中访问可变数量的参数。`va_end()`宏用于清理`va_list`变量。



## `netdev_printk()`

​	可以发现，不管是哪种定义方式，最后都会调用`netdev_printk()`函数，该函数定义如下：

```c
static void __netdev_printk(const char *level, const struct net_device *dev,
			    struct va_format *vaf)
{
	if (dev && dev->dev.parent) {
		dev_printk_emit(level[1] - '0',
				dev->dev.parent,
				"%s %s %s%s: %pV",
				dev_driver_string(dev->dev.parent),
				dev_name(dev->dev.parent),
				netdev_name(dev), netdev_reg_state(dev),
				vaf);
	} else if (dev) {
		printk("%s%s%s: %pV",
		       level, netdev_name(dev), netdev_reg_state(dev), vaf);
	} else {
		printk("%s(NULL net_device): %pV", level, vaf);
	}
}
```

​	`%pV`是专门用来打印`struct va_format`结构体的格式。

> ```
> struct va_format:
> 
> 	%pV
> 
> 	For printing struct va_format structures. These contain a format string
> 	and va_list as follows:
> 
> 	struct va_format {
> 		const char *fmt;
> 		va_list *va;
> 	};
> 
> 	Implements a "recursive vsnprintf".
> 
> 	Do not use this feature without some mechanism to verify the
> 	correctness of the format string and va_list arguments.
> 
> 	Passed by reference.
> ```



# 例子

```c
#include <stdio.h>
#include <stdarg.h>
 
#if 1
#define CHECK_FMT(a, b)	__attribute__((format(printf, a, b)))
#else
#define CHECK_FMT(a, b)
#endif
 
void TRACE(const char *fmt, ...) CHECK_FMT(1, 2);
 
void TRACE(const char *fmt, ...)
{
	va_list ap;
 
	va_start(ap, fmt);
 
	(void)printf(fmt, ap);
 
	va_end(ap);
}
 
int main(void)
{
	TRACE("iValue = %d\n", 6);
	TRACE("iValue = %d\n", "test");
 
	return 0;
}
```

​	注意：需要打开警告信息，即`-Wall`

​	编译结果如下：

```
main.cpp: In function ‘int main()’:
main.cpp:26:31: warning: format ‘%d’ expects argument of type ‘int’, but argument 2 has type ‘const char*’ [-Wformat=]
  TRACE("iValue = %d\n", "test");
```

​	但是如果不使用`__attribute__(format(printf, a, b))`，则编译器不会做检查，也就不会有警告。