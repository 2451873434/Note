# `SPI`

## 1、`SPI`控制器设备注册

```
spi@18011000 {
	compatible = "phytium,spi";
	reg = <0x0 0x18011000 0x0 0x1000>;
	interrupts = <0x0 0x58 0x4>;
	clocks = <0x4>;
	num-cs = <4>;
	#address-cells = <0x1>;
	#size-cells = <0x0>;
	status = "okay";
};
```

​	经过`start_kernel->setup_arch->unfiatten_device_tree`流程后，会对设备树进行解析并把上面的节点转换为`device_node`。

​	`device_node`转换成`platform_device`需要满足以下条件之一：

​	1）该节点必须是根节点的子节点，且该节点必须含有`compatible`属性，则该节点可以转换为`platform_device`。

​	2）含有特殊`compatible`属性的节点的子节点，则该子节点可以转换为`platform_device`。这些特殊的`compatible`属性为：`simple-bus`，`simple-mfd`，`isa`，`arm,amba-bus`。

​	所以该`SPI`控制器节点能够转换成`platform_device`，转换后如下：

```
static struct resource spi_resource[] = {
	{
		.start	= 0x18011000,
		.end	= 0x18011000 + 0x1000,
		.flags	= IORESOURCE_MEM,
	},{
		.start	= xx2irq(0x0, 0x58, 0x4),
		.end	= xx2irq(0x0, 0x58, 0x4),
		.flags	= IORESOURCE_IRQ,
	},
};

struct platform_device pdev = {
	.name		= "spi",
	.dev 		= {
		.of_node = &spi_node,
	},
	.resource	= &spi_resource,
	.num_resources = ARRAY_SIZE(spi_resource),
};
```

## 2、`SPI`控制器驱动注册

