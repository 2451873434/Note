​	`Arm CCA`是在`Armv9`引入的机密计算体系。

## 1、错误可见性下降

​	`CCA`引入`Realm World`，其内存和状态对`Normal World/Hypervisor/OS`均不可见。

传统的`RAS`：

* `OS/Hypervisor`可以直接读取错误寄存器
* 可以解析内存`ECC`、`Synchronous abort`等错误

`CCA`下的`RAS`：

* `Realm`内存错误不能直接暴露给`Normal World`
* `RAS`错误报告必须经过`RMM`



​	`RAS`的诊断路径变为：`Hardware error -> RMM -> Host OS/Hypervisor`。这意味着错误信息可能被过滤或匿名化，`Host OS`可能无法定位具体`Realm`数据结构。

## 2、内存`RAS`处理复杂化

​	`CCA`使用`GPT`来保护内存。

传统`RAS`：

* `OS page offline`
* `kill process`
* `posion page`

`CCA`下的`RAS`：

* `RMM intercept`
* `Realm abort`
* `Host notified`，`Host`不能直接修复`Realm`内存页