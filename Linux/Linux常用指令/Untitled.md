# Linux的4种休眠模式

​	Linux有4种休眠模式（S1，S2，S3，S4），可以通过以下指令进入不同的休眠模式。

```shell
echo on > /sys/power/state
echo standby > /sys/power/state
echo mem > /sys/power/state
echo disk > /sys/power/state
```

![](picture/Linux的4种休眠模式.png)