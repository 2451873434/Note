# `RASv1/RASSAv1/RASv1p1/RASSAv1p1`特性验证

测试项一：`Host OS`应该能正确检测到`RASv1p1`特性

`Host OS`启动后，应该可以检测到`RASv1p1`特性：

`dmesg`应该有如下输出：

```
[	x.xxxxxx]CPU features: detected: RASv1p1 Extension Support
```

测试项二：

`FEAT_RASv1p1 introduces support for System register access to the following RAS System Architecture v1.1 features`：

* `additional ERR<n>MISC<m> registers`
  * `Additional ERXMISC<m>_EL1 System registers`
* `The optional RAS Common Fault Injection Model Extension`
  * `Additional System registers ERXPFGCDN_EL1、ERXPFGCTL_EL1 and ERXPFGF_EL1 and the SCR_EL3.FIEN and HCR_EL2.FIEN trap controls, to support the optional RAS Common Fault Injection Model Extension`

​	第一个新增的功能与`ERXMISC<m>_EL1`系统寄存器相关，第二个新增的功能与`ERXPFGCDN_EL1、ERXPFGCTL_EL1 and ERXPFGF_EL1`系统寄存器相关，因此，可以使用写`ERXPFGCDN_EL1、ERXPFGCTL_EL1 and ERXPFGF_EL1`系统寄存器触发`RAS`错误，然后报错信息中显示`ERXMISC<m>_EL1`的值。通过该测试方法来验证上述两个特性。

1. 获取并安装开源工具system-register-tools； 

2. 确定 RAS 相关寄存器在 registersv8.table 中对应的编码是否与 Tianji2c一致；

   cd msr-arm

   insmod msr.ko

   cp ../registersv8.table ~/.regstable

3. 固件中配置辅助控制寄存器 ACTLR_EL2 和 ACTLR_EL3 的 bit[5]为 1；

4. 在系统下使用system-register-tools工具读 ERXPFGF_EL1寄存器确定支 持错误注入机制以及可纠、可延迟和不可纠错误；  rdasr -p0 -r ERXPFGF_EL1

5. 写ERRSELR_EL1寄存器选择分组0：L1/L2对应的错误记录；  wrasr -p0 -r ERRSELR_EL1 0x0

6. 写 ERXPFGCDN_EL1 寄存器配置写入错误产生计数器的值，在指定个 cycle 之后产生错误；  wrasr -p0 -r ERXPFGCDN_EL1 0x100

7. 写 ERXPFGCTL_EL1 寄存器使能错误产生计数器递减，并分别对可纠 错、可延迟和不可纠错误的产生进行使能；  wrasr -p0 -r ERXPFGCTL_EL1 0x80000040/0x80000020/0x80000002   # 可纠错/可延迟错误/ 不可纠错

8. 对于可纠错需要先配置MISC0寄存器为溢出状态；  wrasr -p0 -r ERXMISC0_EL1 0xff00000000  写溢出  rdasr -p0 -r ERXSTATUS_EL1

9. 查看 ERXSTATUS_EL1 寄存器查看是否有相应错误产生，

   预期：

   查看log是否打印错误信息中是否存在`ERXMISC<m>_EL1`寄存器，RAS错误是否正常上报到OS，报错信息与注错相符。

测试项三：

该测试项测试基本的RAS功能，用于验证RASv1/RASSAv1，理论上测试项二也可以覆盖RASv1/RASSAv1的验证。

```
cd /sys/kernel/debug/apei/einj
echo 1 > notrigger
echo 1 > error_type
echo 1 > error_inject
```

# DoubleFault特性验证

`DoubleFault`特性相关寄存器为`ID_AA64PFR0_EL1`系统寄存器，有关其`bit[31:28]`的描述如下：

| RAS    | Meaning                                                      |
| ------ | ------------------------------------------------------------ |
| 0b0000 | No RAS Extension.                                            |
| 0b0001 | Support for the Reliability, Availability, and Serviceability Extension is implemented. The ESB<br/> instruction and the Error synchronization event are supported |
| 0b0010 | As0b0001, and adds support for:<br/> • IfEL3isimplemented,FEAT_DoubleFault.<br/> • AdditionalERXMISC\<m\>_EL1Systemregisters.<br/> • AdditionalSystemregisters ERXPFGCDN_EL1,ERXPFGCTL_EL1,andERXPFGF_EL1,<br/> and the SCR_EL3.FIEN and HCR_EL2.FIENtrap controls, to support the optional RAS<br/> CommonFault Injection Model Extension.<br/> Error records accessed through System registers conform to RAS System Architecture v1.1, which<br/> includes simplifications to ERR\<n\>STATUS and support for the optional RAS Timestamp and RAS<br/> CommonFault Injection Model Extensions |



​	在 ARM 架构中，没有一个像 x86 那样的、独立的、专门的“Double Fault”处理程序。在Linux ARM架构下，Double Fault的概念与X86有所不同，在x86中，Double Fault是指处理器在尝试处理一个异常时又发生了另一个异常，从而触发一个特定的双重故障异常。而在ARM架构中，没有完全相同的概念，但是存在类似的错误处理机制。ARM架构下的Double Fault处理机制主要是通过异常向量表的不同入口核备用栈来实现的，旨在防止在异常处理过程中发生栈溢出等错误导致系统无法记录错误信息。当异常发生在同步、IRQ、FIQ或SError时，会根据当前异常级别核使用的栈指针来选择不同的处理路径。

​	`SError`（Synchronous Error Interrupt）是 ARM 中用于处理异步外部中止（asynchronous external abort）的异常。这通常是内存系统或其他外部组件报告的严重错误。在处理一个异常时，如果又发生了一个无法被精确报告的严重错误，CPU 可能会将其作为 SError 抛出。SEA（Synchronous External Abort）错误是ARM中用于处理同步外部中止的异常。这种异常通常与内存访问有关，比如加载（load）或存储（store）指令试图访问一个无效的物理地址时，可能会产生SEA。

​	不论是SEA还是SError，都是通过异常向量表进入的异常处理函数。可以通过安装trig_sea.ko/trig_sei.ko模块来触发SEA/SEI异常，即Firstfault。然后内核进入异常处理函数do_sea()/do_serror()，再在异常处理函数do_sea()/do_serror()中加入读取空指针代码段来触发DoubleFault。

​	即SEA/SEI异常为第一个异常（FirstFault），异常处理函数中的空指针访问为第二个异常（DoubleFault）。也可以在自定义模块中加入空地址访问来触发第一个异常，然后在相应的异常处理函数中再同样加入空地址访问来触发第二个异常。

```c
/* trig_sea.c */
#include <linux/module.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/mm.h>
#include <linux/io.h>

#define my_ioremap(addr, size)		ioremap_port((addr), (size), PROT_NORMAL)

static int __init trig_sea_init(void)
{
    void __iomem *vaddr;
    int a;
    
    vaddr = my_ioremap(0x100, 0x1000);
    a = __raw_readl(vaddr);
    
    /*
    // trig_sei.c代码与其基本一致，区别在于读触发sea，写触发sei
    *(int *)vaddr = 1;
    __raw_writel(1, vaddr);
    */
    
    return 0;
}

static void __exit trig_sea_exit(void)
{
    
}

module_init(trig_sea_init);
module_exti(trig_sea_exit);

MODULE_LICENSE("GPL");
```

```c
/* arch/arm64/mm/fault.c */
static int do_sea(unsigned long far, unsigned long esr, struct pt_regs *regs)
{
	const struct fault_info *inf;
	unsigned long siaddr;

    /* 访问空指针触发Double_fault */
    asm volatile(
        "mov x0, #0\n"
        "ldr x1, [x0]\n"
    );
    
	inf = esr_to_fault_info(esr);

	if (user_mode(regs) && IS_ENABLED(CONFIG_ACPI_APEI_SEA)) {
        return 0;
	}

	if (esr & ESR_ELx_FnV) {
		siaddr = 0;
	} else {
		/*
		 * The architecture specifies that the tag bits of FAR_EL1 are
		 * UNKNOWN for synchronous external aborts. Mask them out now
		 * so that userspace doesn't see them.
		 */
		siaddr  = untagged_addr(far);
	}
	arm64_notify_die(inf->name, regs, inf->sig, inf->code, siaddr, esr);

	return 0;
}

/* arch/arm64/kernel/traps.c */
void do_serror(struct pt_regs *regs, unsigned long esr)
{
	/* 访问空指针触发Double_fault */
    asm volatile(
        "mov x0, #0\n"
        "ldr x1, [x0]\n"
    );
    
	/* non-RAS errors are not containable */
	if (!arm64_is_ras_serror(esr) || arm64_is_fatal_ras_serror(regs, esr))
		arm64_serror_panic(regs, esr);
}
```

验证步骤：

1. 进入OS后，手动安装trig_sea.ko/trig_sei.ko模块，触发SEA/SEI异常（或者安装trig_fault.ko触发异常），即FirstFault

   ```
   /* 安装一个即可 */
   insmod trig_sea.ko
   insmod trig_sei.ko
   insmod trig_fault.ko
   ```

2. 触发异常后，内核自动从异常向量表进入相对应的异常处理函数，然后访问空指针触发DoubleFault

预期：

​	系统宕机且有相关异常信息