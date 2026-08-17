# `EPROBE_DEFER`

`EPROBE_DEFER`是`Linux`内核中一个特殊的错误代码，用于设备驱动探测过程中，表示由于依赖资源（例如：时钟、`GPIO`、`regulator`等）暂时不可用，希望稍后重新尝试探测。

`EPROBE_DEFER`机制是`Linux`设备驱动模型的核心特征之一，它使得内核能够动态地处理复杂的设备依赖关系，大大提高了系统的灵活性和可靠性。

## 定义和值

```c
#define EPROBE_DEFER	517
```

## 作用

### 处理设备依赖关系

当驱动在探测阶段发现其依赖的某个资源（由另一个驱动提供）还没有准备好时，返回`-EPROBE_DEFER`会使得内核将驱动探测推迟，并在未来再次尝试探测。这样，内核可以处理驱动之间的依赖关系，而不会让驱动因依赖资源未就绪而初始化失败。

### 解决初始化顺序问题

允许内核优雅地处理驱动之间的依赖关系，而不需要硬编码初始化顺序。

## 使用场景

1、资源依赖：例如，一个设备驱动依赖的`regulator`（电源管理）还没有被注册，驱动可以返回`-EPROBE_DEFER`，这样当`regulator`驱动注册后，内核会尝试探测该设备驱动。

```c
static int stm32_spi_probe(struct platform_device *pdev)
{
    /* ... */
    spi->dma_tx = dma_request_chan(spi->dev, "tx");
	if (IS_ERR(spi->dma_tx)) {
		ret = PTR_ERR(spi->dma_tx);
		spi->dma_tx = NULL;
		if (ret == -EPROBE_DEFER)
			goto err_clk_disable;
    /* ... */
}
```

2、设备节点依赖：在设备树中，如果设备节点引用了另一个节点（例如通过`phandle`），而被引用的节点对应的驱动还未加载，则可以使用`-EPROBE_DEFER`延迟探测。

## 内核处理机制

当驱动返回`-EPROBE_DEFER`时：

1、驱动会将设备添加到延迟探测表

2、内核会定期重新尝试探测这些设备

3、当新驱动注册时，会触发相关依赖设备的重新探测

4、由最大重试限制，避免无限循环

## 注意事项

1、不要滥用：只在真正存在依赖关系时使用

2、错误码传递：某些函数可能直接返回`-EPROBE_DEFER`，应该直接传递这个错误

3、调试：可以使用内核参数`deferred_probe_timeout`控制超时时间

4、查看状态：通过`/sys/kernel/debug/devices_deferred`查看延迟探测的设备列表