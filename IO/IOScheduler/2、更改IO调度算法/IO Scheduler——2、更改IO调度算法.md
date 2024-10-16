# IO Scheduler——2、更改IO调度算法

# 修改IO调度算法

在RHEL5/OEL5以及之后的版本中，可以针对每块磁盘制定I/O Scheduler，修改完毕立刻生效，比如：

```bash
$ cat /sys/block/sda1/queue/scheduler
[noop] anticipatory deadline cfq

# 修改为cfq
$ echo 'cfq' > /sys/block/sda1/queue/scheduler

# 立刻生效
$ cat /sys/block/sda1/queue/scheduler
noop anticipatory deadline [cfq]
```
