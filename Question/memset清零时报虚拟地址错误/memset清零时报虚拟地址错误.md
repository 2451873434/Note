# `memset`清零时报虚拟地址错误

## 问题描述

​	`spi-v2`驱动中`debug-log`存放在`regfile`地址段，由`RV`侧填充`log`信息，且由`AP`侧清空。但是在驱动注册时，首次映射地址并清空时报虚拟地址错误。

```c
fts->log = devm_ioremap(dev, fts->ddr_paddr, fts->log_size);
if (IS_ERR(fts->log)) {
    dev_err(dev, "log_addr is err\n");
    return;
}

memset(fts->log, 0, fts->log_size);
```

```
[    6.338227][ 3] [  T342] Unable to handle kernel paging request at virtual address ffffffc011fc8000
......
[    6.338259][ 7] [  T342] pc : __memset+0x16c/0x188
[    6.338262][ 3] [  T342] lr : spi_phyt_hw_init+0x60/0x80 [spi_phytium_v2]
......
[    6.338274][ 3] [  T342] Call trace:
[    6.338275][ 3] [  T342]  __memset+0x16c/0x188
[    6.338277][ 3] [  T342]  spi_phyt_add_host+0x198/0x210 [spi_phytium_v2]
[    6.338279][ 3] [  T342]  spi_phyt_probe+0x2d4/0x448 [spi_phytium_plat_v2]
......
```

## 问题原因

以下为`AI`分析的可能原因，不一定正确，请仔细甄别。

1、地址对齐：`devm_ioremap`映射的是非缓存内存，有严格的对齐要求。`memset`可能会使用一些需要对齐的指令（如`SEE/AVX`），如果地址没有按照要求对齐，就会导致错误。

2、内存类型：非缓存内存不允许使用一些优化指令，而`memset`可能会根据编译选项使用这些指令。例如，`memset`可能会使用`SSE`指令来快速设置内存，但这些指令在非缓存内存上是不允许的，会导致处理器异常。

3、地址检测：内核可能对非缓存内存的访问有更严格的检查，比如使用正确的访问函数（如`ioread32/iowrite32`）。直接使用`memset`可能会被内核视为错误的访问方式。

## 解决方法

**方法1**：

使用`devm_ioremap_wc()`代替`devm_ioremap()`函数。`devm_ioremap_wc()`映射的是写合并内存，其可能允许使用非对齐访问。

```c
fts->log = devm_ioremap_wc(dev, fts->ddr_paddr, fts->log_size);
if (IS_ERR(fts->log)) {
    dev_err(dev, "log_addr is err\n");
    return;
}

memset(fts->log, 0, fts->log_size);
```

**方法2**：

使用`memset_io()`代替`memset()`函数。直接使用`memset()`可能在任何一种映射上都不安全，只是`devm_ioremap_wc()`的写合并映射可能在某些架构上侥幸工作，不具有可移植性。

```c
fts->log = devm_ioremap(dev, fts->ddr_paddr, fts->log_size);
if (IS_ERR(fts->log)) {
    dev_err(dev, "log_addr is err\n");
    return;
}

memset_io(fts->log, 0, fts->log_size);
```

