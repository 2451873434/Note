#include <linux/types.h>
#include <linux/kernel.h>
#include <linux/delay.h>
#include <linux/ide.h>
#include <linux/init.h>
#include <linux/module.h>
#include <linux/errno.h>
#include <linux/gpio.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/of.h>
#include <linux/of_address.h>
#include <linux/of_gpio.h>
#include <linux/platform_device.h>
#include <linux/miscdevice.h>
#include <asm/mach/map.h>
#include <asm/uaccess.h>
#include <asm/io.h>

#define MISCKY_NAME    "KY-015"

typedef unsigned char u8;

struct miscky_dev{
	dev_t devid;			/* 设备号 	 */
	struct cdev cdev;		/* cdev 	*/
	struct class *class;	/* 类 		*/
	struct device *device;	/* 设备 	 */
	int ky_gpio;
};

struct miscky_dev miscky;

static u8 miscky_read_data(void)
{
    int i;
    u8 result = 0;

    for (i = 0; i < 8; i++) {
        while(gpio_get_value(miscky.ky_gpio) == 0);
        
	udelay(30);
        if (gpio_get_value(miscky.ky_gpio) == 1)
            result |= (1 << (8 - i));
        while(gpio_get_value(miscky.ky_gpio) == 1);
    }
    return result;
}

static int ky_gpio_init(struct device_node *nd)
{
	int ret, i;
	u8 value;
	u8 buf[5] = {0};
	int a=0, b=0, c=0;

	/* 从设备树中获取GPIO */
	miscky.ky_gpio = of_get_named_gpio(nd, "ky-gpios", 0);
	if(!gpio_is_valid(miscky.ky_gpio)) {
		printk("miscky：Failed to get ky-gpio\n");
		return -EINVAL;
	}
	
	/* 申请使用GPIO */
	ret = gpio_request(miscky.ky_gpio, "ky");
	if(ret) {
		printk("ky: Failed to request ky-gpio\n");
		return ret;
	}
	
    gpio_direction_output(miscky.ky_gpio, 1);
    return 0;
}

static int miscky_open(struct inode *inode, struct file *filp)
{
	return 0;
}

static ssize_t miscky_read(struct file *filp, char __user *buf, size_t cnt, loff_t *offt)
{
    printk(KERN_ERR "%s:%d\n", __func__, __LINE__);
    int i;
    int ret = 0;
    u8 k_buf[5]={0};

    gpio_set_value(miscky.ky_gpio, 0);
    mdelay(25);
    gpio_set_value(miscky.ky_gpio, 1);
    udelay(20);
    gpio_direction_input(miscky.ky_gpio);
    while(gpio_get_value(miscky.ky_gpio) == 1) {
	    udelay(10);
    }
    while(gpio_get_value(miscky.ky_gpio) == 0) {
	    udelay(10);
    }
    while(gpio_get_value(miscky.ky_gpio) == 1) {
	    udelay(10);
    }
    for (i = 0; i < 5; i++)
      k_buf[i] = miscky_read_data();

    gpio_direction_output(miscky.ky_gpio, 1);

    for (i = 0; i < 5; i++)
	    printk(KERN_ERR "buf[%d]=0x%x\n",i, k_buf[i]);

    copy_to_user(buf, k_buf, 5);

    return 0;
}

static struct file_operations miscky_fops = {
	.owner = THIS_MODULE,
	.open = miscky_open,
	.read = miscky_read,
};

static struct miscdevice ky_miscdev = {
	.minor = MISC_DYNAMIC_MINOR,
	.name = MISCKY_NAME,
	.fops = &miscky_fops,
};

static int miscky_probe(struct platform_device *pdev)
{
	int ret = 0;

	printk("ky driver and device was matched!\r\n");

	/* 初始化ky */
	ret = ky_gpio_init(pdev->dev.of_node);
	if(ret < 0)
		return ret;
		
	/* 一般情况下会注册对应的字符设备，但是这里我们使用MISC设备
  	 * 所以我们不需要自己注册字符设备驱动，只需要注册misc设备驱动即可
	 */
	ret = misc_register(&ky_miscdev);
	if(ret < 0){
		printk("misc device register failed!\r\n");
		goto free_gpio;
	}

	return 0;
	
free_gpio:
	gpio_free(miscky.ky_gpio);
	return -EINVAL;
}

static int miscky_remove(struct platform_device *dev)
{
	/* 释放ky */
	gpio_free(miscky.ky_gpio);

	/* 注销misc设备 */
	misc_deregister(&ky_miscdev);
	return 0;
}

 /* 匹配列表 */
 static const struct of_device_id ky_of_match[] = {
     { .compatible = "alientek,ky" },
     { /* Sentinel */ }
 };
 
 /* platform驱动结构体 */
static struct platform_driver ky_driver = {
     .driver     = {
         .name   = "stm32mp1-ky",         /* 驱动名字，用于和设备匹配 */
         .of_match_table = ky_of_match, /* 设备树匹配表          */
     },
     .probe      = miscky_probe,
     .remove     = miscky_remove,
};

/*
 * @description	: 驱动出口函数
 * @param 		: 无
 * @return 		: 无
 */
static int __init miscky_init(void)
{
	return platform_driver_register(&ky_driver);
}

/*
 * @description	: 驱动出口函数
 * @param 		: 无
 * @return 		: 无
 */
static void __exit miscky_exit(void)
{
	platform_driver_unregister(&ky_driver);
}

module_init(miscky_init);
module_exit(miscky_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("ALIENTEK");
MODULE_INFO(intree, "Y");
