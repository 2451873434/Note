# `modpost: vmlinux: section mismatch in reference: xxx(section: .text) -> xxx(section: .init.text)`
**问题原因**
一个在`test`节区中的函数或变量引用了一个在`.init.text`节区中的函数或变量。
在`Linux`内核中，`.init.text`节区用于存放初始化代码，这些代码在内核初始化完成后会被释放（通过`free_initmem()`）。因此，如果正常的代码（在`.text`节区中）引用了`.init.text`中的代码，那么当`.init.text`被释放后，该引用就会变成悬空指针，导致内核崩溃。
以如下示例为例，就会出现该报错：
```c
static int __init test_func(void) { }

/* 以下引用就会报警告 */
static int test_probe(struct platform_device *pdev)
{
	test_func();
}

/* 以下引用不会报警告 */
static int __init test_init(void)
{
	test_func();
}
```
