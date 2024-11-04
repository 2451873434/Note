# `bitmap`

> 参考链接：
>
> [linux内核中的bitmap](https://blog.csdn.net/qqliyunpeng/article/details/53412802)



​	笔者在接触`misc`驱动时阅读到`misc_register()`函数中一段代码如下：

```c
if (is_dynamic) {
	int i = find_first_zero_bit(misc_minors, DYNAMIC_MINORS);

	if (i >= DYNAMIC_MINORS) {
		err = -EBUSY;
        goto out;
	}
	misc->minor = DYNAMIC_MINORS - i - 1;
	set_bit(i, misc_minors);
}
```

​	该段代码的功能为自动分配子设备号，其巧妙的运用了`bitmap`相关的一些函数来实现该功能。

> ​	在阅读完本文后，笔者建议可以去了解`input`子系统，其中很多地方应用了`bitmap`的知识。

## 1、简介

​	`bitmap`用于实现`bool`数组，标识一个事件发生还是没发生。在此例中，其就是用来标识某个子设备号是否被使用。`bitmap`将一片连续的空间作为一个数据类型，其中的成员都是1位，长度是`bitmap`的容量。

## 2、`bitmap`

```c
#define BITS_PER_BYTE 8
#define DIV_ROUND_UP(n,d) (((n) + (d) - 1) / (d))
#define BITS_TO_LONGS(nr)	DIV_ROUND_UP(nr, BITS_PER_BYTE * sizeof(long))
#define DECLARE_BITMAP(name,bits) \
	unsigned long name[BITS_TO_LONGS(bits)]
static DECLARE_BITMAP(misc_minors, 64);
```

​	根据以上定义，可以解析成：

```
/* 在32位系统下 */
#define DECLARE_BITMAP(name, bits)  \
	unsigned long name[(bits+31)/32]

/* 在64位系统下 */
#define DECLARE_BITMAP(name, bits)  \
	unsigned long name[(bits+63)/64]
```

​	在此例中，`misc_minor`定义为`unsigned long misc_minor[1]`。

## 3、`find_first_zero_bit()`

```c
#define find_first_zero_bit(addr, size) find_next_zero_bit((addr), (size), 0)
```

​	`addr`：`bitmap`的首地址，即`unsigned long name[]`的首地址

​	`size`：`bitmap`中含有的`bit`位的总和

​	`find_first_zero_bit()`函数的功能是找到第一个为0的`bit`位，相应`find_next_zero_bit()`函数的功能是找到从某一位开始的第一个为0的`bit`位。我们并不需要详细了解该函数的代码，只需要知道并使用其功能即可。

## 4、`set_bit()`

```c
static inline void __set_bit(int nr, volatile unsigned long *addr)
{
	unsigned long mask = BIT_MASK(nr);
	unsigned long *p = ((unsigned long *)addr) + BIT_WORD(nr);
 
	*p  |= mask;
}
/* 找到在单 unsigned long 元素中的第几位 */
#define BIT_MASK(nr)		(1UL << ((nr) % BITS_PER_LONG))
/* 找到操作的位所在的unsigned long数组中的地址 */
#define BIT_WORD(nr)		((nr) / BITS_PER_LONG)
#define BITS_PER_LONG 32 /* 32位系统下 */
#define BITS_PER_LONG 64 /* 64位系统下 */
```

​	`set_bit()`函数将`bitmap`中的第`nr`位置1。（从第0位开始）

## 5、`clear_bit()`

```c
static inline void __clear_bit(int nr, volatile unsigned long *addr)
{
	unsigned long mask = BIT_MASK(nr);
	unsigned long *p = ((unsigned long *)addr) + BIT_WORD(nr);
 
	*p &= ~mask;
}
#define BIT_MASK(nr)		(1UL << ((nr) % BITS_PER_LONG))
#define BIT_WORD(nr)		((nr) / BITS_PER_LONG)
```

​	`clear_bit()`函数将`bitmap`中的第`nr`位清0。（从第0位开始）

## 7、`change_bit()`

```c
static inline void __change_bit(int nr, volatile unsigned long *addr)
{
	unsigned long mask = BIT_MASK(nr);
	unsigned long *p = ((unsigned long *)addr) + BIT_WORD(nr);
 
	*p ^= mask;
}
 
#define BIT_MASK(nr)		(1UL << ((nr) % BITS_PER_LONG))
```

​	`change_bit()`函数将`bitmap`中某一位取反。

## 8、`test_bit()`

```c
static inline int test_bit(int nr, const volatile unsigned long *addr)
{
	return 1UL & (addr[BIT_WORD(nr)] >> (nr & (BITS_PER_LONG-1)));
}
#define BIT_WORD(nr)		((nr) / BITS_PER_LONG)
```

​	`test_bit()`函数判断某一位有没有被置1

## 9、其它接口

```c
/**
 * __test_and_set_bit - 设置一个位并且返回它原先的值
 * @nr: 要设置的位/bitmap中的哪一位
 * @addr: bitmap首地址
 */
static inline int __test_and_set_bit(int nr, volatile unsigned long *addr);
 
/**
 * __test_and_clear_bit - 清空一个位并且返回它的原先的值
 * @nr: bitmap中的哪一位
 * @addr: bitmap的首地址
 */
static inline int __test_and_clear_bit(int nr, volatile unsigned long *addr);
 
/**
 * __test_and_clear_bit - 取反某一位并返回它的原先的值
 * @nr: bitmap中的哪一位
 * @addr: bitmap的首地址
 */
static inline int __test_and_change_bit(int nr, volatile unsigned long *addr)
```

