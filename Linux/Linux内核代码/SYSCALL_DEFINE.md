# `Linux`系统调用`SYSCALL_DEFINE`详解

> 参考链接：[Linux系统调用SYSCALL_DEFINE详解](https://blog.csdn.net/weixin_43798887/article/details/118930476)
>
> 涉及到的宏有：`SYSCALL_DEFINEx`、`SYSCALL_METADATA`、`__SYSCALL_DEFINEx`、`__MAP`、`__MAPx`、`__SC_XXX`



​	`Linux`的系统调用在内核中的入口函数都是`sys_xxx`，但是如果我们拿着内核源码去搜索的话，会发现找不到`sys_xxx`的函数定义，这是因为`Linux`的系统调用对应的函数全部都是由`SYSCALL_DEFINE`相关的宏来定义。

```c
#define SYSCALL_DEFINE1(name, ...) SYSCALL_DEFINEx(1, _##name, __VA_ARGS__)
#define SYSCALL_DEFINE2(name, ...) SYSCALL_DEFINEx(2, _##name, __VA_ARGS__)
#define SYSCALL_DEFINE3(name, ...) SYSCALL_DEFINEx(3, _##name, __VA_ARGS__)
#define SYSCALL_DEFINE4(name, ...) SYSCALL_DEFINEx(4, _##name, __VA_ARGS__)
#define SYSCALL_DEFINE5(name, ...) SYSCALL_DEFINEx(5, _##name, __VA_ARGS__)
#define SYSCALL_DEFINE6(name, ...) SYSCALL_DEFINEx(6, _##name, __VA_ARGS__)
```

​	`SYSCALL_DEFINEx`中的`x`代表的是系统调用参数个数。

```c
#define SYSCALL_DEFINEx(x, sname, ...)				\
	SYSCALL_METADATA(sname, x, __VA_ARGS__)			\
	__SYSCALL_DEFINEx(x, sname, __VA_ARGS__)

#define SYSCALL_METADATA(sname, nb, ...)			\
	static const char *types_##sname[] = {			\
		__MAP(nb,__SC_STR_TDECL,__VA_ARGS__)		\
	};							\
	static const char *args_##sname[] = {			\
		__MAP(nb,__SC_STR_ADECL,__VA_ARGS__)		\
	};							\
	SYSCALL_TRACE_ENTER_EVENT(sname);			\
	SYSCALL_TRACE_EXIT_EVENT(sname);			\
	static struct syscall_metadata __used			\
	  __syscall_meta_##sname = {				\
		.name 		= "sys"#sname,			\
		.syscall_nr	= -1,	/* Filled in at boot */	\
		.nb_args 	= nb,				\
		.types		= nb ? types_##sname : NULL,	\
		.args		= nb ? args_##sname : NULL,	\
		.enter_event	= &event_enter_##sname,		\
		.exit_event	= &event_exit_##sname,		\
		.enter_fields	= LIST_HEAD_INIT(__syscall_meta_##sname.enter_fields), \
	};							\
	static struct syscall_metadata __used			\
	  __section("__syscalls_metadata")			\
	 *__p_syscall_meta_##sname = &__syscall_meta_##sname;

#ifndef __SYSCALL_DEFINEx
#define __SYSCALL_DEFINEx(x, name, ...)					\
	__diag_push();							\
	__diag_ignore(GCC, 8, "-Wattribute-alias",			\
		      "Type aliasing is used to sanitize syscall arguments");\
	asmlinkage long sys##name(__MAP(x,__SC_DECL,__VA_ARGS__))	\
		__attribute__((alias(__stringify(__se_sys##name))));	\
	ALLOW_ERROR_INJECTION(sys##name, ERRNO);			\
	static inline long __do_sys##name(__MAP(x,__SC_DECL,__VA_ARGS__));\
	asmlinkage long __se_sys##name(__MAP(x,__SC_LONG,__VA_ARGS__));	\
	asmlinkage long __se_sys##name(__MAP(x,__SC_LONG,__VA_ARGS__))	\
	{								\
		long ret = __do_sys##name(__MAP(x,__SC_CAST,__VA_ARGS__));\
		__MAP(x,__SC_TEST,__VA_ARGS__);				\
		__PROTECT(x, ret,__MAP(x,__SC_ARGS,__VA_ARGS__));	\
		return ret;						\
	}								\
	__diag_pop();							\
	static inline long __do_sys##name(__MAP(x,__SC_DECL,__VA_ARGS__))
#endif /* __SYSCALL_DEFINEx */
```

​	可以看到，`SYSCALL_DEFINEx`宏涉及的东西有点多，我们以一个实例`sys_reboot`函数为例，其声明在`include/linux/syscalls.h`，定义在`kernel/reboot.c`。

```c
/* include/linux/syscalls.h */
asmlinkage long sys_reboot(int magic1, int magic2, unsigned int cmd,
				void __user *arg);

/* kernel/reboot.c */
SYSCALL_DEFINE4(reboot, int, magic1, int, magic2, unsigned int, cmd,
		void __user *, arg)
{
 	/* code... */   
}
```

​	结合上述宏定义展开如下：

```c
static const char *types_reboot[] = {
	__MAP(4,__SC_STR_TDECL,__VA_ARGS__)
};
static const char *args_reboot[] = {
	__MAP(4,__SC_STR_ADECL,__VA_ARGS__)
};
SYSCALL_TRACE_ENTER_EVENT(reboot);
SYSCALL_TRACE_EXIT_EVENT(reboot);
static struct syscall_metadata __used
  __syscall_meta_reboot = {
	.name 		= "sysreboot",
	.syscall_nr	= -1,	/* Filled in at boot */
	.nb_args 	= 4,
	.types		= 4 ? types_reboot : NULL,
	.args		= 4 ? args_reboot : NULL,
	.enter_event	= &event_enter_reboot,
	.exit_event	= &event_exit_reboot,
	.enter_fields	= LIST_HEAD_INIT(__syscall_meta_reboot.enter_fields),
};
static struct syscall_metadata __used
  __section("__syscalls_metadata")
 *__p_syscall_meta_reboot = &__syscall_meta_reboot;

__diag_push();
__diag_ignore(GCC, 8, "-Wattribute-alias",
	      "Type aliasing is used to sanitize syscall arguments");
asmlinkage long sysreboot(__MAP(4,__SC_DECL,__VA_ARGS__))
	__attribute__((alias(__stringify(__se_sysreboot))));
ALLOW_ERROR_INJECTION(sysreboot, ERRNO);
static inline long __do_sysreboot(__MAP(4,__SC_DECL,__VA_ARGS__));
asmlinkage long __se_sysreboot(__MAP(4,__SC_LONG,__VA_ARGS__));
asmlinkage long __se_sysreboot(__MAP(4,__SC_LONG,__VA_ARGS__))
{
	long ret = __do_sysreboot(__MAP(4,__SC_CAST,__VA_ARGS__));
	__MAP(4,__SC_TEST,__VA_ARGS__);
	__PROTECT(4, ret,__MAP(4,__SC_ARGS,__VA_ARGS__));
	return ret;
}
__diag_pop();
static inline long __do_sysreboot(__MAP(4,__SC_DECL,__VA_ARGS__))
```

​	其中`__MAP`宏定义如下：

```c
/*
 * __MAP(n, m, t1, a1, t2, a2, ..., tn, an) will expand to
 *    m(t1, a1), m(t2, a2), ..., m(tn, an)
 */
#define __MAP0(m,...)
#define __MAP1(m,t,a,...) m(t,a)
#define __MAP2(m,t,a,...) m(t,a), __MAP1(m,__VA_ARGS__)
#define __MAP3(m,t,a,...) m(t,a), __MAP2(m,__VA_ARGS__)
#define __MAP4(m,t,a,...) m(t,a), __MAP3(m,__VA_ARGS__)
#define __MAP5(m,t,a,...) m(t,a), __MAP4(m,__VA_ARGS__)
#define __MAP6(m,t,a,...) m(t,a), __MAP5(m,__VA_ARGS__)
#define __MAP(n,...) __MAP##n(__VA_ARGS__)
```

​	同样，笔者以`__MAP(4,__SC_LONG,__VA_ARGS__)`为例，做展开后如下：

```c
__MAP4(__SC_LONG,__VA_ARGS__)
```

​	其中`__VA_ARGS__`就是`int, magic1, int, magic2, unsigned int, cmd, void __user *, arg`，所以继续展开后如下：

```c
__SC_LONG(int,magic1), __SC_LONG(int, magic2), __SC_LONG(unsigned int, cmd), __SC_LONG(void __user *, arg)
```

​	其中`__SC_LONG`宏定义如下：

```c
#define __SC_LONG(t, a) __typeof(__builtin_choose_expr(__TYPE_IS_LL(t), 0LL, 0L)) a
```

​	`__builtin_choose_expr `是`GCC`的一个内置函数，类似于C语言中的条件运算符`?:`。如果`__TYPE_IS_LL(t)` 为真，那么表达式类型为`long long`，否则为`long`。因此，最后展开后如下：

```c
long magic1, long magic2, long cmd, long arg
```

​	最终整个宏展开如下：

```c
__diag_push();
__diag_ignore(GCC, 8, "-Wattribute-alias", "Type aliasing is used to sanitize syscall arguments");

// 1. 实际的系统调用函数声明（alias到安全版本）
asmlinkage long sys_reboot(int magic1, int magic2, unsigned int cmd, void __user * arg)
    __attribute__((alias("__se_sys_reboot")));

// 2. 允许错误注入
ALLOW_ERROR_INJECTION(sys_reboot, ERRNO);

// 3. 内联函数的提前声明
static inline long __do_sys_reboot(int magic1, int magic2, unsigned int cmd, void __user * arg);

// 4. 安全系统调用函数的声明和定义
asmlinkage long __se_sys_reboot(long magic1, long magic2, long cmd, long arg);
asmlinkage long __se_sys_reboot(long magic1, long magic2, long cmd, long arg)
{
    // 4.1 调用实际的实现函数（进行类型转换）
    long ret = __do_sys_reboot((int)magic1, (int)magic2, (unsigned int)cmd, (void __user *)arg);
    
    // 4.2 参数检查（可能是空操作或指针验证）
    (void)magic1; (void)magic2; (void)cmd; (void)arg;
    
    // 4.3 保护机制（防止竞争条件等）
    __PROTECT(4, ret, magic1, magic2, cmd, arg);
    
    return ret;
}

__diag_pop();

// 5. 实际的系统调用实现（内联函数）
static inline long __do_sys_reboot(int magic1, int magic2, unsigned int cmd, void __user * arg)
{
    /* code... */
}
```

