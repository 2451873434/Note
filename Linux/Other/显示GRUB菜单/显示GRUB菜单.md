# 显示`GRUB`菜单

​	有时候有些系统盘在启动的时候不会显示`GRUB`菜单而直接进系统，但是有时候又需要去更换内核、修改`vmlinuz-xxx`或者`initrd-xxx`等。

​	修改`/etc/default/grub`文件，如下：

```
/* 修改前 */
GRUB_TIMEOUT_STYLE=hidden
GRUB_TIMEOUT=0

/* 修改后 */
GRUB_TIMEOUT_STYLE=menu
GRUB_TIMEOUT=5
GRUB_TERMINAL="seri"
GRUB_SERIAL_COMMAND="serial --unit=0 --speed=115200 --word=8 --parity=no --stop=1"
```

