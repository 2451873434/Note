# 为什么qspi间接读写不能通过设置no-direct-mapping属性来实现

## 问题现象

​	仔细阅读`qspi`控制器驱动代码，可以发现下面这样几段描述。

```c
/**
 * Direct mapping is supported only when all flashes under the controller
 * are of the same size and the mapping address is continuous. For those
 * cases which flashes are of different sizes, the driver offered a non-dirmap
 * mem_ops with which read/write ops is executed through command port.
 */
static struct spi_controller_mem_ops phytium_qspi_mem_ops_nodirmap = {
	.adjust_op_size = phytium_qspi_adjust_op_size,
	.supports_op	= phytium_qspi_supports_op,
	.exec_op	= phytium_qspi_exec_op,
};

static int phytium_qspi_probe(struct platform_device *pdev)
{
    /* ... */
	qspi->nodirmap = device_property_present(dev, "no-direct-mapping");
	ctrl->mem_ops = qspi->nodirmap ?
			&phytium_qspi_mem_ops_nodirmap :
			&phytium_qspi_mem_ops;
	/* ... */
}
```

​	根据描述可知，我们可以通过在设备树的`qspi`控制器节点描述中加入`no-direct-mapping`属性来设置`qspi`为间接模式。间接读写都是通过`phytium_qspi_exec_op()`函数实现。但是实际上，仔细阅读间接读写的实现代码可以发现，其所谓的间接读写仅支持小于8字节数据量的读写操作，代码如下。

```c
static int phytium_qspi_write_port(struct phytium_qspi *qspi,
				   const u8 *buf, const size_t len)
{
	u32 bouncebuf[2] = { 0 };

	if (len > PHYTIUM_QSPI_MAX_XFER_SZ) {
		dev_err(qspi->dev, "WRITE data exceeds 8 bytes.\n");
		return -EINVAL;
	}

	memcpy(bouncebuf, buf, len);

	if (len > 4)
		writel_relaxed(bouncebuf[1], qspi->io_base + QSPI_HD_PORT_REG);
	writel_relaxed(bouncebuf[0], qspi->io_base + QSPI_LD_PORT_REG);

	return 0;
}

static int phytium_qspi_read_port(struct phytium_qspi *qspi,
				  u8 *buf, size_t len)
{
	u32 bouncebuf[2] = { 0 };

	if (len > PHYTIUM_QSPI_MAX_XFER_SZ) {
		dev_err(qspi->dev, "READ data exceeds 8 bytes.\n");
		return -EINVAL;
	}

	/* Dummy write to LD_PORT register and issue READ ops*/
	writel_relaxed(0, qspi->io_base + QSPI_LD_PORT_REG);

	/* Read data */
	bouncebuf[0] = readl_relaxed(qspi->io_base + QSPI_LD_PORT_REG);
	if (len > 4)
		bouncebuf[1] = readl_relaxed(qspi->io_base + QSPI_HD_PORT_REG);

	memcpy(buf, bouncebuf, len);

	return 0;
}

static int phytium_qspi_exec_op(struct spi_mem *mem,
				const struct spi_mem_op *op)
{
    /* ... */
	if (op->data.dir == SPI_MEM_DATA_IN) {
		ret = phytium_qspi_read_port(qspi, op->data.buf.in, op->data.nbytes);
		if (ret) {
			dev_err(qspi->dev, "Failed to read data from the port.\n");
			goto out;
		}
	} else if (op->data.dir == SPI_MEM_DATA_OUT) {
		ret = phytium_qspi_write_port(qspi, op->data.buf.out, op->data.nbytes);
		if (ret) {
			dev_err(qspi->dev, "Failed to write data to the port.\n");
			goto out;
		}

	}
    /* ... */
}
```

​	也就是说，如果读写数据量不大于8字节，那么通过在设备树的`qspi`控制器节点中加入`no-direct-mapping`属性可以实现间接读写，但是如果数据量大于8字节，则需要额外编写一套逻辑代码实现间接读写功能。