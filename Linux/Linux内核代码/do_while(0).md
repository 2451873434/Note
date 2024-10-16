# Linux内核中用到do while(0)的用途

> 参考链接：
>
> [Linux内核中do{...}while(0)的意义](https://blog.csdn.net/ibless/article/details/81638420)



​	`Linux`内核和其它一些开源代码中，经常会遇到下面这样格式的代码：

```c
do {
    /* ... */
} while(0)
```

​	这样的代码一看就不是一个循环，`do{...}while(0)`表面上看在这里一点用都没有，那么为什么要这么用呢？实际上，`do{...}while(0)`的作用远大于美化你的代码。

**1.辅助定义复杂的宏，避免引用的时候出错**

​	举例来说，假设你需要定义下面这样一个宏：

```c
#define DOSOMEFUNC()	\
	func1();			\
	func2();
```

​	这个宏的本意是，当调用`DOSOMEFUNC()`时，`func1()`函数和`func2()`函数都会被调用。但是如果你用如下方式调用：

```c
if (a > 0)
    DOSOMEFUNC();	/* 注意这个分号，这是习惯写法 */
```

​	因为宏在预处理的时候会直接被展开，实际上展开后的代码如下：

```c
if (a > 0)
    func1();
func2();
```

​	这显然和我们本意不一样，将会导致程序出错。那么仅仅使用`{}`将`func1()`和`func2()`包起来行吗？我们在写代码的时候都习惯在语句右边加上分号，如果在宏中使用`{}`，展开后如下：

```c
if (a > 0)
{
    func1();
    func2();
};
```

​	显然，这样编译无法通过。

​	综上所述，正因如此很多人才采用了`do{...}while(0)`，这样宏被展开后，才会保留初始语义。`GCC`提供了`Statement-Expressions`用以替代`do{...}while(0)`，所以也可以如下定义宏：

```c
#define DOSOMETHING() ({\
        foo1(); \
        foo2(); \
})
```

**2.避免使用`goto`对程序流进行统一的控制**

​	有些函数中，在函数`return`之前我们经常会进行一些收尾的工作，比如用`free()`函数释放掉一块由`malloc()`函数申请的内存。

```c
int foo()
{
    somestruct* ptr = malloc(...);
 
    /* dosomething */
    if(error)
    {
        goto END;
    }
 
    /* dosomething */
    if(error)
    {
        goto END;
    }
    
    /* dosomething */
 
END:
    free(ptr);
    return 0;
 
}
```

​	由于`goto`不符合软件工程的结构化，而且有可能使得代码难懂，所以很多人都不倡导使用，那这个时候就可以用`do{...}while(0)`来进行统一的管理：

```c
int foo()
{
    somestruct* ptr = malloc(...);
 
    do{
        /* dosomething */
        if(error)
        {
            break;
        }
 
        /* dosomething */
        if(error)
        {
            break;
        }
        
        /* dosomething */
    }while(0);
 
    free(ptr);
    return 0;
}
```

​	这里将函数主体使用`do{...}while(0)`包含起来，使用`break`来代替`goto`，后续的处理工作在`while`之后，就能够达到同样的效果。

**3.避免空宏引起的`warning`**

​	内核中由于不同架构的限制，很多时候会用到空宏，在编译的时候，空宏会给出`warning`，为了避免这样的`warning`，就可以使用`do{...}while(0)`来定义空宏：

```c
#define EMPTYMICRO do{}while(0)
```

**4.定义一个单独的函数块来实现复杂的操作**

​	当你的功能很复杂，变量很多你又不愿意增加一个函数的时候，使用`do{...}while(0)`并将代码写在里面，里面可以定义变量而不用考虑变量名会同函数之前或之后的重复。