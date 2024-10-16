# 获取CPU型号

> 参考链接：[基于ARM架构的芯片获取CPU信息(cpuID)的多种方法](https://blog.csdn.net/buknow/article/details/107721094)

## 问题场景

​	内核驱动新增的某项功能，但是只有某些`cpu`芯片是支持该功能的。内核是否存在接口函数来识别`cpu`芯片型号，从而通过识别出的信息来确定是否支持开启该项功能。

## 解决方法

### 确定机器的`cpuID`

​	如果不清楚芯片的`cpuID`，可以在OS下使用如下指令来读取：

```shell
$ cat /proc/cpuinfo
processor	: 0
model name	: FT-2000/4 
BogoMIPS	: 96.00
Features	: half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt lpae evtstrm aes pmull sha1 sha2 crc32
CPU implementer	: 0x70
CPU architecture: aarch64
CPU variant	: 0x1
CPU part	: 0x663
CPU revision	: 3
```

​	以上是对`cpuID`的拆分解析后的信息，`cpuID`的内容格式如下：`Implementer(31:24) | Variant(23:20) | Architecture(19:16) | Part Number(15:4) | Revision(3:0)`。其各项解释如下：

```c
/* Implementer: venter，销售ID */
#define ARM_CPU_IMP_ARM			0x41
#define ARM_CPU_IMP_APM			0x50
#define ARM_CPU_IMP_CAVIUM		0x43
#define ARM_CPU_IMP_BRCM		0x42
#define ARM_CPU_IMP_QCOM		0x51
#define ARM_CPU_IMP_NVIDIA		0x4E
#define ARM_CPU_IMP_FUJITSU		0x46
#define ARM_CPU_IMP_HISI		0x48
#define ARM_CPU_IMP_APPLE		0x61
#define ARM_CPU_IMP_PHYTIUM		0x70

/* Variant: 大版本号 */

/* Architecture: 架构版本 */
#define CPU_ARCH_UNKNOWN	0
#define CPU_ARCH_ARMv3		1
#define CPU_ARCH_ARMv4		2
#define CPU_ARCH_ARMv4T		3
#define CPU_ARCH_ARMv5		4
#define CPU_ARCH_ARMv5T		5
#define CPU_ARCH_ARMv5TE	6
#define CPU_ARCH_ARMv5TEJ	7
#define CPU_ARCH_ARMv6		8
#define CPU_ARCH_ARMv7		9
#define CPU_ARCH_ARMv7M		10

/* Part Number: 产品代码 */
#define ARM_CPU_PART_CORTEX_A57		0xD07
#define ARM_CPU_PART_CORTEX_A72		0xD08
#define ARM_CPU_PART_CORTEX_A53		0xD03
#define ARM_CPU_PART_CORTEX_A73		0xD09
#define ARM_CPU_PART_CORTEX_A75		0xD0A
#define ARM_CPU_PART_CORTEX_A35		0xD04
#define ARM_CPU_PART_CORTEX_A55		0xD05
#define ARM_CPU_PART_CORTEX_A76		0xD0B
#define ARM_CPU_PART_NEOVERSE_N1	0xD0C
#define ARM_CPU_PART_CORTEX_A77		0xD0D
#define QCOM_CPU_PART_KRYO_2XX_GOLD	0x800
#define QCOM_CPU_PART_KRYO_2XX_SILVER	0x801
#define QCOM_CPU_PART_KRYO_3XX_SILVER	0x803
#define QCOM_CPU_PART_KRYO_4XX_GOLD	0x804
#define QCOM_CPU_PART_KRYO_4XX_SILVER	0x805
#define PHYTIUM_CPU_PART_FTC661		0x661
#define PHYTIUM_CPU_PART_FTC662		0x662
#define PHYTIUM_CPU_PART_FTC663		0x663
#define PHYTIUM_CPU_PART_FTC664		0x664

/* Revision: 小版本号 */
```

## 获取`cpuID`

​	内核提供`read_cpuid_id()`函数来获取`cpuID`，其定义如下：

```c
static inline u32 __attribute_const__ read_cpuid_id(void)
{
	return read_cpuid(MIDR_EL1);
}
```

​	一般情况下，我们只用获取`Implementer`，`Architecture`和`Part Number`这三个信息即可，内核也提供了通用的方法来获取它们：

```c
#define MIDR_CPU_MODEL(imp, partnum) (((imp) << 24) | (0xf << 16) | ((partnum) << 4))

#define MIDR_CPU_MODEL_MASK ((0xff << 24) | (0xf < 16) | (0xfff < 4))
#define MIDR_PHYTIUM_FTC663 MIDR_CPU_MODEL(ARM_CPU_IMP_PHYTIUM, PHYTIUM_CPU_PART_FTC_663)

if ((read_cpuid() & MIDR_CPU_MODEL_MASK) == MIDR_PHYTIUM_FTC663)
    return true;
```

> 以上宏和函数均在`arch/arm64/include/asm/cputype.h`中，如果需要添加新的`cpu`芯片的`cpuID`，则在该文件中添加即可。