# `uboot`常见问题

```
load usb 0:1 0x90100000 tpm/d3000m/Image-v11
load usb 0:1 0x90000000 tpm/d3000m/pd2408-devboard-i2s.dtb
setenv bootargs console=ttyAMA1,115200 earlycon=pl011,0x18002000 root=/dev/nvme0n1p3  rw
booti 0x90100000 - 0x90000000
```

## `ERROR: image is not a fdt - must RESET the board to recover`

**问题现象**

​	加载设备树和内核镜像时并没有报错，在使用`bootm`指令启动后报错，如下所示：

```
PD2408#load usb 0:1 0x90000000 /tpm/D3000M-testA.dtb
17046 bytes read in 1125 ms (14.6 KiB/s)
PD2408#load usb 0:1 0x90100000 /tpm/uImage
48702016 bytes read in 216 ms (215 MiB/s)
PD2408#bootm 0x90100000 -:- 0x90000000
## Booting kernel from Legacy Image at 90100000
   Image Name:
   Created:      2026-01-04 9:18:52 UTC
   Image Type:   AArch64 Linux Kernel Image(uncompressed)
   Data size:    48701952 Bytes = 46.4 MiB
   Load Address: 90000000
   Entry Point:  90000000
   Verifying checksum ...OK
## Flattened Device Tree blob at 90000000
   Booting using the fdt blob at 0x90000000
Working FDT set to 90000000
   Loading Kernel Image to 90000000
ERROR: image is not a fdt - must RESET the board to recover
```

**问题原因**

​	虽然在加载内核镜像时，我们把`uImage`加载到了`0x90100000`地址，但是从`Load Address`地址来看，会将内核镜像加载到`0x90000000`，而我们在`bootm`之前又将设备树加载到按同样的`0x90000000`地址，因此之前加载成功的设备树信息会被内核镜像覆盖，从而导致出现了`ERROR: image is not a fdt - must RESET the board to recover`报错。

**解决方法**

​	在生成`uImage`时，修改其`Load Address`和`Entry Point`地址为`0x80080000`。

​	或者使用`Image`替代`uImage`，同时使用`booti`命令替代`bootm`