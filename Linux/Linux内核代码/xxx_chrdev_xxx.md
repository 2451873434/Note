# `xxx_chrdev_xxx`

> 参考链接：
>
> [一文搞懂内核中有关cdev的各种函数](https://blog.csdn.net/liangzc1124/article/details/120070931)



​	内核提供了三个函数来注册一组字符设备编号，这三个函数分别是`register_chrdev()`、`register_chrdev_region()`、`alloc_chrdev_region()`，区别如下：

## 1、`register_chrdev()`

```c
static inline int register_chrdev(unsigned int major, const char *name,
				  const struct file_operations *fops)
```

​	`major`：主设备号

​	`name`：设备名

​	`fops`：文件操作方法结构体

​	返回值：如果是静态分配，成功返回0，失败返回负值；如果是动态分配，成功返回动态分配的主设备号，失败返回负值

​	较老的内核注册的形式，`linux-2.4`内核版本之前采用的注册方式。`register_chrdev()`可以实现静态和动态注册两种方法，主要是通过判断给定的主设备号是否为0来进行区别，为0的时候为动态注册，否则为静态注册。

> ​	该函数存在一个很大的缺点：每注册一个字符设备，还会连续注册`0-255`个次设备号，并使它们绑定在同一个`file_operations`操作方法结构体上。在大多数情况下，都只用极少的次设备号，所以会浪费很多资源。
>
> ​	如`input`驱动中，存在同一个主设备号，不同次设备号，并且它们的`file_operations`都不一样，表现为`/dev/input/event*`，`event0`和`event1`的`file_operations`不一样，这种情况下就不能直接使用`register_chrdev()`函数。

## 2、`register_chrdev_region()`

```c
int register_chrdev_region(dev_t from, unsigned count, const char *name)
```

​	`from`：要分配的设备编号范围的初始值，明确了主设备号和起始次设备号

​	`count`：设备个数，即次设备号个数

​	`name`：相关联的设备名称（可在`/proc/devices`目录下看到），也即本组设备的驱动名称

​	`register_chrdev_region()`函数是在事先知道要使用的主、次设备号时使用的，可在`proc/devices`目录下查看有哪些设备号可用。

​	`register_chrdev_region() + cdev`实现的就是`register_chrdev()`的静态注册。

> ​	内核中的`input`子系统采用的就是`register_chrdev_region() + cdev`来实现设备的静态注册，所有`/dev/input/event*`设备的主设备号均为13。

## 3、`alloc_chrdev_region()`

```c
int alloc_chrdev_region(dev_t *dev, unsigned baseminor, unsigned count,
			const char *name)
```

​	`dev`：这是一个输出型参数，所以是指针形式，和`register_chrdev_region()`函数的第一个参数不同。获得一个分配到的设备号，可以用`MAJOR`和`MINOR`宏将主、次设备号提取打印出来，以便查看自动分配的是多少。

​	`baseminor`：起始次设备号

​	`count`：次设备号的个数

​	`name`：驱动的名字

​	返回值：小于0，表示自动分配失败，为0表示成功

​	`alloc_chrdev_region()`函数自动分配未被使用的设备号。

​	`alloc_chrdev_region() + cdev`实现的就是`register_chrdev()`的动态注册。

## 4、`cdev`

```c
struct cdev {
	struct kobject kobj;
	struct module *owner;
	const struct file_operations *ops;
	struct list_head list;
	dev_t dev;
	unsigned int count;
};
```

​	`cdev`用于注册驱动到内核中。

### 4.1 `cdev_alloc()`

```c
struct cdev *cdev_alloc(void)
{
	struct cdev *p = kzalloc(sizeof(struct cdev), GFP_KERNEL);
	if (p) {
		INIT_LIST_HEAD(&p->list);
		kobject_init(&p->kobj, &ktype_cdev_dynamic);
	}
	return p;
}
```

​	为`cdev`的结构体分配空间。

### 4.2 `cdev_init()`

```c
void cdev_init(struct cdev *cdev, const struct file_operations *fops)
{
	memset(cdev, 0, sizeof *cdev);
	INIT_LIST_HEAD(&cdev->list);
	kobject_init(&cdev->kobj, &ktype_cdev_default);
	cdev->ops = fops;
}
```

​	将`struct cdev`类型的结构体变量和`file_operation`结构体进行绑定。如果之前使用过`cdev_alloc()`函数，则就可以直接使用`cdev->ops = fops`来进行绑定，不需要使用`cdev_alloc()`。在`cdev_init()`函数中，除了`cdev->ops = fops`之外的其它操作都在`cdev_alloc()`函数中做了。

### 4.3 `cdev_add()`

```c
int cdev_add(struct cdev *p, dev_t dev, unsigned count)
{
	int error;

	p->dev = dev;
	p->count = count;

	error = kobj_map(cdev_map, dev, count, NULL,
			 exact_match, exact_lock, p);
	if (error)
		return error;

	kobject_get(p->kobj.parent);

	return 0;
}
```

​	向内核里面添加一个驱动，注册驱动。

### 4.4 `cdev_del()`

```c
void cdev_del(struct cdev *p)
{
	cdev_unmap(p->dev, p->count);
	kobject_put(&p->kobj);
}
```

​	释放`cdev`结构体空间，`cdev_del()`函数内部是能知道你的`struct cdev`定义的对象是用的堆内存还是数据段内存的。

## 5、`xxx_chrdev_xxx()`再分析

```c
int __register_chrdev(unsigned int major, unsigned int baseminor,
		      unsigned int count, const char *name,
		      const struct file_operations *fops)
{
    /* ... */
	cd = __register_chrdev_region(major, baseminor, count, name);

	cdev = cdev_alloc();

	cdev->owner = fops->owner;
	cdev->ops = fops;
	kobject_set_name(&cdev->kobj, "%s", name);

	cdev_add(cdev, MKDEV(cd->major, baseminor), count);

	cd->cdev = cdev;

	return major ? 0 : cd->major;
}
```

```c
int register_chrdev_region(dev_t from, unsigned count, const char *name)
{
    /* ... */
	__register_chrdev_region(MAJOR(n), MINOR(n),
			       next - n, name);
    /* ... */
}
```

```c
int alloc_chrdev_region(dev_t *dev, unsigned baseminor, unsigned count,
			const char *name)
{
	/* ... */
	cd = __register_chrdev_region(0, baseminor, count, name);
	/* ... */
}
```

