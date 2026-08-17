# `SCMI`使用

> 参考文档：
>
> [《`E2000-scmi使用.txt`》]



## 1、`power`

### 1.1 电源设置

​	电源设置指令如下：

```
scmi mhu [protocol_id] 0x4 0(表示同步，必须是0) [domain_id] [state]
```

​	`protocol_id`：`power`为`0x11`。

| 描述    | `protocol_id` |
| ------- | ------------- |
| `POWER` | `0x11`        |
| `RESET` | `0x16`        |
| `CLOCK` | `0x14`        |
| `PERF`  | `0x13`        |

​	`domain_id`：

| `drv`        | `id` | `flag`                                                       |
| ------------ | ---- | ------------------------------------------------------------ |
| `clust0_drv` | 0    | `CLUSTER0`（1<<0）                                           |
| `clust1_drv` | 1    | `CLUSTER1`（1<<0）                                           |
| `clust2_drv` | 2    | `PWR_FLAG_CLUST2`（1<<0）<br />`PWR_FLAG_CLUST2C0`（1<<1）<br />`PWR_FLAG_CLUST2C1`（1<<2） |
| `gsd_drv`    | 3    | `PWR_FLAG_GSD`（1<<0）<br />`PWR_FLAG_GSD_DC`（1<<1）<br />`PWR_FLAG_GSD_DP`（1<<2）<br />`PWR_FLAG_GSD_SATA`（1<<3）<br />`PWR_FLAG_GSD_GMU_0`（1<<4）<br />`PWR_FLAG_GSD_GMU_1`（1<<5）<br />`PWR_FLAG_GSD_GMU_2`（1<<6）<br />`PWR_FLAG_GSD_GMU_3`（1<<7） |
| `peu_drv`    | 4    | `PWR_FLAG_PEU`（1<<0）<br />`PWR_FLAG_PEU_X4`（1<<1）<br />`PWR_FLAG_PEU_X1_0`（1<<2）<br />`PWR_FLAG_PEU_X1_1`（1<<3）<br />`PWR_FLAG_PEU_X1_2`（1<<4） |
| `psu_drv`    | 5    | `PWR_FLAG_PSU`（1<<0）<br />`PWR_FLAG_PSU_SATA`（1<<1）<br />`PWR_FLAG_PSU_USB3_0`（1<<2）<br />`PWR_FLAG_PSU_USB3_1`（1<<3）<br />`PWR_FLAG_PSU_PX1_0`（1<<4）<br />`PWR_FLAG_PSU_PX1_1`（1<<5） |
| `lsd_drv`    | 6    | `PWR_FLAG_LSD`（1<<0）<br />`PWR_FLAG_LSD_NAND`（1<<1）      |
| `vpu_drv`    | 7    | `PWR_FLAG_VPU`（1<<0）                                       |
| `dmu_drv`    | 8    | `PWR_FLAG_DMU`（1<<0）                                       |
| `ocn_drv`    | 9    | `PWR_FLAG_OCN_MMU`（1<<0）<br />`PWR_FLAG_OCN_DMA`（1<<1）<br />`PWR_FLAG_MAIN_OCN`（1<<2） |
| `sce_drv`    | a    | `PWR_FLAG_TOPSUB_SCE`（1<<0）                                |

​	`state`：`bit[30]`，为1表示上电，为0表示下电。`bit[27:0]`为要操作的位，为1表示要操作，为0表示不操作。

​	如下为`psu`的上下电的示例：

```
上电psu的bit1和bit2:
scmi mhu 0x11 0x4 0 5 0x40000006

下电psu的bit1和bit2:
scmi mhu 0x11 0x4 0 5 0x6
```

### 1.2 电源状态获取

​	电源状态获取指令如下：

```
scmi mhu 0x11 0x5 [domain_id]
```

​	`domain_id`：同上。

​	返回值：为0表示对应的位是下电状态，为1表示对应的位是上电状态。

## 2、`reset`

​	复位部件的指令如下：

```
scmi mhu [protocol_id] 0x4 [domain_id] [flag] [reset_state]
```

​	`protocol_id`：同上。`reset`为`0x16`。

​	`domain_id`：

| `drv`        | `id` | `flag`                                                       |
| ------------ | ---- | ------------------------------------------------------------ |
| `clust0_drv` | 0    | `CLUSTER0`（1<<0）                                           |
| `clust1_drv` | 1    | `CLUSTER1`（1<<0）                                           |
| `clust2_drv` | 2    | `RST_FLAG_CLUSTER2C0`（1<<0）<br />`RST_FLAG_CLUSTER2C1`（1<<1）<br />`RST_FLAG_CLUSTER2`（1<<2） |
| `gsd_drv`    | 3    | `RST_FLAG_CFGCLK`（`1<<11`）<br />`RST_FLAG_GSD`（1<<10）<br />`RST_FLAG_SATA`（1<<9）<br />`RST_FLAG_DC`（1<<8）<br />`RST_FLAG_GMU_0`（1<<7）<br />`RST_FLAG_GMU_1`（1<<6）<br />`RST_FLAG_GMU_2`（1<<5）<br />`RST_FLAG_GMU_3`（1<<4）<br />`RST_FLAG_GMU_0`（1<<3）<br />`RST_FLAG_GMU_1`（1<<2）<br />`RST_FLAG_GMU_2`（1<<1）<br />`RST_FLAG_GMU_3`（1<<0） |
| `peu_drv`    | 4    | `RST_FLAG_PEU_C3`（1<<5）<br />`RST_FLAG_PEU_C2`（1<<4）<br />`RST_FLAG_PEU_C1`（1<<3）<br />`RST_FLAG_PEU_C0`（1<<2）<br />`RST_FLAG_PEU_WP`（1<<1）<br />`RST_FLAG_PEU`（1<<0） |
| `psu_drv`    | 5    | `RST_FLAG_PEU_PSU_C1`（1<<8）<br />`RST_FLAG_PEU_PSU_C0`（1<<7）<br />`RST_FLAG_PSU_SERDES1`（1<<6）<br />`RST_FLAG_PSU_SERDES0`（1<<5）<br />`RST_FLAG_PSU_VHUB`（1<<4）<br />`RST_FLAG_PSU_SATA`（1<<3）<br />`RST_FLAG_PSU_USB3`（1<<2）<br />`RST_FLAG_PSU_PCIE`（1<<1）<br />`RST_FLAG_PSU_NCC`（1<<0） |
| `lsd_drv`    | 6    | `RST_FLAG_WDT_1_WP`（1<<2）<br />`RST_FLAG_WDT_0_WP`（1<<1）<br />`RST_FLAG_LSD`（1<<0） |
| `vpu_drv`    | 7    | `RST_FLAG_VPU`（1<<0）                                       |
| `dmu_drv`    | 8    | `RST_FLAG_DMU`（1<<0）                                       |
| `ocn_drv`    | 9    | `RST_FLAG_DMAC1`（1<<11）<br />`RST_FLAG_DMAC0`（1<<10）<br />`RST_FLAG_SMMU`（1<<9）<br />`RST_FLAG_OCM`（1<<8）<br />`RST_FLAG_NCC`（1<<7）<br />`RST_FLAG_SEMA`（1<<6）<br />`RST_FLAG_INT`（1<<5）<br />`RST_FLAG_JPEG`（1<<4）<br />`RST_FLAG_FDBG`（1<<3）<br />`RST_FLAG_RMS`（1<<2）<br />`RST_FLAG_RAS_WP`（1<<1）<br />`RST_FLAG_OCN`（1<<0） |
| `sce_drv`    | a    | `RST_FLAG_SCE`（1<<0）                                       |

​	`flag`：为0表示只释放，为1表示复位并释放，为2表示只复位。

​	`reset_state`：`bit[31]`，为1表示自行指定模块内信号，为0表示模块内全部信号。

## 3、`clock`

### 3.1 获取时钟域描述

​	获取时钟域描述命令如下：

```
scmi mhu [protocol_id] 0x4 [domain_id] [skip]
```

​	`protocol_id`：同上。`clock`为`0x14`。

​	`domain_id`：

| `domain_id` | id   |
| ----------- | ---- |
| `clk_ocn`   | 0    |
| `clk_dmu`   | 1    |
| `clk_dc0`   | 2    |
| `clk_dc1`   | 3    |
| `clk_se`    | 4    |

​	`skip`：跳过几个，默认为0表示不跳过。

### 3.2 设置时钟域频率

​	设置时钟域频率的命令如下：

```
scmi mhu [protocol_id] 0x5 [flag] [domain_id] [freq]
```

​	`protocol_id`：同上。`clock`为`0x14`。

​	`flag`：保持为0。

​	`domain_id`：同上。

​	`freq`：设置的时钟域频率，为16进制，单位为`HZ`。

### 3.3 获取时钟域频率

​	获取时钟域频率命令如下：

```
scmi mhu [protocol_id] 0x6 [domain_id]
```

## 4、`perf`

### 4.1 获取调频等级描述

​	获取调频等级描述命令如下：

```
scmi mhu [protocol_id] 0x4 [domain_id] [skip]
```

​	`protocol_id`：同上。`perf`为`0x13`。

​	`domain_id`：

| `domain_id`  | id   |
| ------------ | ---- |
| `clust0_drv` | 0    |
| `clust1_drv` | 1    |
| `clust2_drv` | 2    |

​	`skip`：表示跳过几个，默认为0，表示不跳过。

### 4.2 设置调频等级

```
scmi mhu [protocol_id] 0x7 [domain_id] [perf_level]
```

​	`protocol_id`：同上。

​	`domain_id`：同上。

​	`perf_level`：频率等级。

### 4.3 获取调频等级

```
scmi mhu [protocol_id] 0x8 [domain_id]
```

