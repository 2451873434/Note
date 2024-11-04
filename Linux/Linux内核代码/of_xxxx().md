在设备树的根节点`/`下创建一个`stm32mp1_led`节点。

```
stm32mp1_led {
	compatible = "atkstm32mp1-led";
	status = "okay";
	reg = <0X50000A28 0X04 /* RCC_MP_AHB4ENSETR */
		   0X5000A000 0X04 /* GPIOI_MODER */
		   0X5000A004 0X04 /* GPIOI_OTYPER */
		   0X5000A008 0X04 /* GPIOI_OSPEEDR */
		   0X5000A00C 0X04 /* GPIOI_PUPDR */
		   0X5000A018 0X04 >; /* GPIOI_BSRR */
};
```

​	使用该设备树进入`OS`后，在`/sys/firmware/devicetree/base`目录下存在`stm32mp1_led`目录，`stm32mp1_led`目录下又存在`compatible`、`name`、`reg`和`status`文件。（`name`为`stm32mp1_led`）

## `of_find_node_by_path()`

​	`of_find_node_by_path()`函数就是以`/sys/firmware/devicetree/base`为基础目录进行查找，如下：

```c
struct device_node *nd = of_find_node_by_path("/stm32mp1_led");
```

## `of_find_node_by_name()`

​	`of_find_node_by_name()`函数就是以`/sys/firmware/devicetree/base/stm32mp1_led/name`为基础目录进行查找。

```c
struct device_node *nd = of_find_node_by_path("stm32mp1_led");
```

## `of_iomap()`

```c
void __iomem *of_iomap(struct device_node *node, int index);
```

​	通过设备树的设备节点直接进行设备内存区间的`ioremap()`，`index`是内存段的索引。

```c
struct void __iomem *addr0 = of_iomap(nd, 0);
/* ... */
struct void __iomem *addr5 = of_iomap(nd, 5);

/* 取消映射 */
iounmap(addr0);
```

