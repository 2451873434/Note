# `IIO`子系统——`IIO`框架及`IIO`数据结构

> 参考链接：
>
> [Linux设备驱动之IIO子系统——IIO框架及IIO数据结构](https://www.cnblogs.com/yongleili717/p/10744252.html)



​	工业`I/O`（`IIO`）是专用于数模转换器（`DAC`）和模数转换器（`ADC`）的内核子系统。随着越来越多的具有不同代码实现的传感器（具有模拟到数字或数字到模拟功能的测量设备）分散在内核源上，收集它们变得必要。这就是`IIO`框架以通用的方式所做的事情。

​	加速度计，陀螺仪，电流/电压测量芯片，光传感器，压力传感器等都属于`IIO`系列器件。

​	`IIO`模型基于设备和通道架构：

​		1）设备代表芯片本身。它是层次结构的顶级。

​		2）通道代表设备的单个采集线。设备可以具有一个或多个通道。

​	`IIO`芯片是物理和硬件传感器或转换器。它作为字符设备暴露给用户空间，以及包含一组文件的`sysfs`目录条目，其中一些文件代表通道。单个通道用单个`sysfs`文件条目表示。

​	下面是从用户空间与`IIO`驱动程序交互的两种方式：

​		1）`/sys/bus/iio/iio:deviceX/`：表示传感器及其通道

​		2）`/dev/iio:deviceX`：表示导出设备事件和数据缓冲区的字符设备

​	驱动程序使用`IIO`核心公开的一组工具和`API`来管理硬件并向`IIO`核心报告处理，然后，`IIO`子系统通过`sysfs`接口和字符设备将整个底层机制抽象到用户空间，用户可以在其上执行系统调用。`IIO`框架如下：

![](picture/IIO框架.png)

​	上图显示了如何在内核和用户空间之间组织`IIO`框架。驱动程序使用`IIO`核心公开的一组工具和`API`来管理硬件并向`IIO`核心报告处理。然后`IIO`子系统通过`sysfs`接口或字符设备将整个底层机制抽象到用户空间，用户可以在其上执行系统调用。

​	`IIO API`分布在多个头文件中，如下：

```c
#include <linux/iio/iio.h>    /* mandatory */
#include <linux/iio/sysfs.h>  /* mandatory since sysfs is used */
#include <linux/iio/events.h> /* For advanced users, to manage iio events */
#include <linux/iio/buffer.h> /* mandatory to use triggered buffers */
#include <linux/iio/trigger.h>/* Only if you implement trigger in your driver (rarely used)*/
```

## 1、关键数据结构

### 1.1 `iio_dev`

​	`IIO`子系统使用结构体`iio_dev`来描述一个具体`IIO`设备，`iio_dev`结构体定义如下（只列出部分重要参数）：

```c
struct iio_dev {
	int				modes;
	int				currentmode;
	struct device			dev;

	struct iio_buffer		*buffer;
	struct list_head		buffer_list;
	int				scan_bytes;
	struct mutex			mlock;

	const unsigned long		*available_scan_masks;
	unsigned			masklength;
	const unsigned long		*active_scan_mask;
	bool				scan_timestamp;
	unsigned			scan_index_timestamp;
	struct iio_trigger		*trig;
	bool				trig_readonly;
	struct iio_poll_func		*pollfunc;
	struct iio_poll_func		*pollfunc_event;

	struct iio_chan_spec const	*channels;
	int				num_channels;

	struct list_head		channel_attr_list;
	struct attribute_group		chan_attr_group;
	const char			*name;
	const struct iio_info		*info;
	clockid_t			clock_id;
	struct mutex			info_exist_lock;
	const struct iio_buffer_setup_ops	*setup_ops;
	struct cdev			chrdev;
};
```

* `modes`：设备支持的模式，常用的可选模式如下：
  * `INDIO_DIRECT_MODE`：提供`sysfs`接口
  * `INDIO_BUFFER_TRIGGERED`：支持硬件触发器
  * 其它
* `currentmode`：当前模式
* `buffer`：缓冲区
* `scan_bytes`：捕获并馈送到缓冲区的字节数
* `avaliable_sacn_mask`：