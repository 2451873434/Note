# `Load Address`和`Entry Point`对同一类型机器是不是不变

## 问题现象

​	此前，笔者一直以为对同一类型的机器来说，其`Load Address`和`Entry Point`是固定不变的，因为在此之前笔者接触过的所有`E2000`型号的板子其`Load Address`和`Entry Point`都是`0x80080000`。然而，笔者后续发现一个有趣的现象，就是在使用其他人编译的`uImage`在`E2000`机器上测试时，发现其`Load Address`和`Entry Point`的值竟然为`0x90100000`，并且也能正常进系统。

```
/* E2000机器使用其他人的uImage */
## Booting kernel from Legacy Image at 90100000 ...
   Image Name:   
   Image Type:   AArch64 Linux Kernel Image (uncompressed)
   Data Size:    49179136 Bytes = 46.9 MiB
   Load Address: 90100000
   Entry Point:  90100000
   Verifying Checksum ... OK
   
/* E2000机器使用自己编译的uImage */
## Booting kernel from Legacy Image at 80080000 ...
   Image Name:   
   Image Type:   AArch64 Linux Kernel Image (uncompressed)
   Data Size:    19128832 Bytes = 18.24 MiB
   Load Address: 80080000
   Entry Point:  80080000
   Verifying Checksum ... OK
```
