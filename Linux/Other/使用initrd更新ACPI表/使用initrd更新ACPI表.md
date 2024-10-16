# 使用initrd更新ACPI表

> 参考链接：
>
> [ACPI AML debug and override ACPI tables using initrd](https://blog.csdn.net/dachai/article/details/91398387)



​	本文介绍`ACPICA debugger tools`，如`acpidbg`、`acpidump`、`acpiexec`等，并演示如何使用这些工具，配合`initrd`在不重新加载`firmware`的情况下，修改`ACPI table`。

​	如果读者的目的是想要动态修改`ACPI`表，则直接阅读第三节的内容即可。

## 1、acpidbg

​	`acpidbg`是一个`runtime`调试`AML code`的工具，不过是在`Linux 4.13`中才引入的。

### 1.1 how to enable

​	参考`Documentation/acpi/aml-debugger.txt`文档。使用`acpidbg`工具需要`kernel`和`userspace`都支持。

**kernel**

​	编译内核时，需要设置：

​	`CONFIG_ACPI_DEBUGGER=y`

​	`CONFIG_ACPI_DEBUGGER_USER=m`

​	编译内核后在`drivers/acpi/`目录下得到`acpi_dbg.ko`模块。

**userspace**

```shell
# 生成userspace下使用的acpidbg工具
$ cd tools/power/acpi/tools/acpidbg/
$ make
```

> 不同内核中`acpidbg`工具存放的位置不同，也可能是在`tools/acpi/power/acpi/acpidbg/`目录中。
>
> 此外，`acpidump`工具一般和`acpidbg`放在一块，即`tools/power/acpi/tools/acpidump/`目录下。

### 1.2 how to start userspace debugger

​	使用上述编译的内核启动系统，并将`acpi_dbg.ko`模块和`acpidbg`工具拷贝到某个目录下，然后完成如下操作：

```shell
$ mount -t debugfs none /sys/kernel/debug
$ ls
acpi_dbg.ko acpidbg
$ insmod acpi_dbg.ko
```

### 1.3 commond supported

​	`acpidbg`启动之后，可以输入`help`，查看`acpidbg`支持的`commond`，如下：

```shell
$ acpidbg
- help
Summary of AML Debugger Commands
Namespace Access:			//访问namespace的命令
  	Businfo                             			//Display system bus info
  	Disassemble <Method>                		//Disassemble a control method
  	Find <AcpiName> (? is wildcard)     	//Find ACPI name(s) with wildcards
  	Integrity                           				//Validate namespace integrity
  	Methods                             			//Display list of loaded control methods
  	Namespace [Object] [Depth]          		//Display loaded namespace tree/subtree
  	Notify <Object> <Value>             		//Send a notification on Object
Objects [ObjectType]                		//Display summary of all objects or just given type
Owner <OwnerId> [Depth]             		//Display loaded namespace by object owner
 	Paths                               Display full pathnames of namespace objects
  	Predefined                          Check all predefined names
  	Prefix [<Namepath>]                 Set or Get current execution prefix
  	References <Addr>                   Find all references to object at addr
  	Resources [DeviceName]              Display Device resources (no arg = all devices)
  	Set N <NamedObject> <Value>         Set value for named integer
  	Template <Object>                   Format/dump a Buffer/ResourceTemplate
  	Type <Object>                       Display object type

Control Method Execution:
  1) Evaluate <Namepath> [Arguments]     			//Evaluate object or control method
  2) Execute <Namepath> [Arguments]      			//Synonym for Evaluate
  3) Debug <Namepath> [Arguments]        			//Single-Step a control method

Miscellaneous:
  Allocations                         			//Display list of current memory allocations
  Dump <Address>|<Namepath> [Byte|Word|Dword|Qword]        
  Handlers 						//Info about global handlers
  Help [Command]                      		//This help screen or individual command
  History                             			//Display command history buffer
  Level <DebugLevel>] [console]       	//Get/Set debug level for file or console
  Locks                               			//Current status of internal mutexes
  Osi [Install|Remove <name>]         	//Display or modify global _OSI list
  Quit or Exit                        			//Exit this command
  Stats <SubCommand>                  	//Display namespace and memory statistics
     Allocations                      Display list of current memory allocations
     Memory                           Dump internal memory lists
     Misc                             Namespace search and mutex stats
     Objects                          Summary of namespace objects
     Sizes                            Sizes for each of the internal objects
     Stack                            Display CPU stack usage
     Tables                           Info about current ACPI table(s)
  Tables                              Display info about loaded ACPI tables
  ! <CommandNumber>                   Execute command from history buffer
  !!                                  Execute last command again

Method and Namespace Debugging:
  Trace <State> [<Namepath>] [Once]   Trace control method execution
     Enable                           Enable all messages
     Disable                          Disable tracing
     Method                           Enable method execution messages
     Opcode                           Enable opcode execution messages
  Test <TestName>                     Invoke a debug test
     Objects                          Read/write/compare all namespace data objects
     Predefined                       Validate all ACPI predefined names (_STA, etc.)
  Execute predefined                  Execute all predefined (public) methods

Control Method Single-Step Execution:
  Arguments (or Args)                 Display method arguments
  Breakpoint <AmlOffset>              Set an AML execution breakpoint
  Call                                Run to next control method invocation
  Go                                  Allow method to run to completion
  Information                         Display info about the current method
  Into                                Step into (not over) a method call
  List [# of Aml Opcodes]             Display method ASL statements
  Locals                              Display method local variables
  Results                             Display method result stack
  Set <A|L> <#> <Value>               Set method data (Arguments/Locals)
  Stop                                Terminate control method
  Tree                                Display control method calling tree
  <Enter>                             Single step next AML opcode (over calls)

```

​	`acpidbg`启动之后，输入各指令的输出示例如下：

```shell
- namespace \_SB.PWRB
	ACPI Namespace (from PWRB (00000000570a7360) subtree):
	 0  _HID Integer      0000000086484fc8 01 = 000000000C0CD041
	 0  _UID Integer      000000008432cef4 01 = 00000000000000AA
 	 0  _STA Integer      00000000699fce6e 01 = 000000000000000B
	 0  _PRW Method       00000000467154ae 01 Args 0 Len 0009 Aml 00000000f0406bd4
	Namespace node count: 4
- execute \_SB.PWRB._STA		//execute _STA  method
	Evaluating \_SB.PWRB._STA
	Evaluation of \_SB.PWRB._STA returned object 000000005d4a43c1, external buffer length 18
	 [Integer] = 000000000000000B
- handlers：		//list handlers info
   Operation Region Handlers at the namespace root:
   		SystemMemory (00) : Default   (000000008e3627f4)
   		SystemIO (01) : Default   (00000000c26e80d4)
   		PCI_Config (02) : Default   (00000000df357aeb)
   		EmbeddedControl (03) : None
   		SMBus (04) : None
   		SystemCMOS (05) : None
   		PCIBARTarget (06) : None
   		IPMI (07) : None
   		GeneralPurposeIo (08) : None
   		GenericSerialBus (09) : None
   		DataTable (7E) : Default   (00000000b76a34e6)
   		FunctionalFixedHW (7F) : None
   Fixed Event Handlers:
   		PM_Timer (00) : None
   		GlobalLock (01) : User      (00000000c25964bf)
   		PowerButton (02) : User      (00000000d0879d19)
   		SleepButton (03) : None
   		RealTimeClock (04) : User      (00000000dbb9df24)
   Miscellaneous Global Handlers:
   		System Notifications : User      (0000000030e91327)
   		Device Notifications : User      (0000000061dc2179)
   		ACPI Table Events : User      (000000005fb8bcf3)
   		Control Method Exceptions : User      (0000000075b0eefe)
   		OSI Invocations : User      (0000000096a26980)
   Operation Region Handlers for specific devices:
   		PCI_Config (02) : Default (00000000df357aeb) Device Name: \_SB.PCI0 (0000000099b391d1)
   		SystemCMOS (05) : User (00000000787d56eb) Device Name: \_SB.PCI0.LPCB.RTC (00000000bece04ca)
   		GenericSerialBus (09) : User (00000000289e2622) Device Name: \_SB.PCI0.SBUS (0000000061eb7af3)
   		SystemIO (01) : User (0000000097b46fee) Device Name: \_SB.PCI0.SBUS (0000000061eb7af3)
   		GenericSerialBus (09) : User (00000000289e2622) Device Name: \_SB.PCI0.GFX0 (0000000099865817)

```

### 1.4 退出`userspace debugger`

```shell
# 以下三种方式均可退出
$ acpidbg
- quit
- exit
- (ctrl + c)

$ rmmod acpi_dbg
```

## 2、ACPICA tools

​	以上提到的`acpidbg`工具是直到`Linux 4.13`才引入的，这之前的老版本内核就不适用该工具了。不过不用担心，`Linux 4.13`之前的内核提供了很多`ACPICA tools`，包括`acpidump`、`acpiexec`、`acpixtract`等工具，也能帮助我们对`AML code`进行调试。

**1.获取所有的`ACPI table`**

```shell
$ acpidump > acpi.log
```

**2.提取DSDT和SSDT信息**

```shell
$ acpixtract acpi.log
```

​	该命令会从`acpi.log`中摘取`DSDT`和所有的`SSDT`信息，生成`dsdt.dat`和`ssdt.dat`文件。`DSDT`和`SSDT`是`device configuration table`，构成了整个`ACPI namespace`，包括所有的`device node`信息。

**3.反编译`dsdt`和`ssdt`文件**

```shell
$ iasl -d dsdt.dat
$ ls
dsdt.dat dsdt.dsl
```

​	得到`DSDT`和`SSDT`相应的`dsl`文件。

**4.查看`ACPI table`描述**

​	使用`vim`打开`dsdl.dsl`即可查看`ACPI table`。

```html
scope(\_SB) {
	Device (PWRB)  {
		Name (_HID, EisaId ("PNP0C0C") /* Power Button Device */)  
		Name (_UID, 0xAA)  
		Name (_STA, 0x0B)
		Method (_PRW, 0, NotSerialized)  {
			Return (GPRW (0x1B, 0x03))
		}
	}
}
```

## 3、利用`initrd`修改`ACPI table`

​	参考文档`Documentations/acpi/initrd_table_override.txt`。

​	如果内核设置了`CONFIG_ACPI_TABLE_UPGRADE=y`，那么就可以通过`initrd`修改或新增`ACPI table`。除了`RSDP`、`FACS`这两个表之外的其他`ACPI table`都可以用这种方式来修改。

### 3.1 获取当前的`DSDT table`

```shell
$ acpidump > acpi.log
$ acpixtract -a acpi.log
# 解析得到dsdt.dsl文件
$ iasl -d dsdt.dat
```

​	此外还有一种更简单的方法来获取`dsdt.dsl`文件，只需要用到`iasl`这个一个工具即可，如下：

```shell
$ cd /sys/firmware/acpi/table
$ cp DSDT /tmp/
$ cd /tmp/
# 解析得到DSDT.dsl文件
$ iasl -d DSDT
```

### 3.2 修改`ACPI table`

​	修改`ACPI table`其实就是修改`dsdt.dsl`文件，可以使用`vim`工具打开`dsdt.dsl`文件进行修改。比如将`SPI1`控制器的`_HID`从`PHTY000E`修改成`PHYT000E`，`_UID`从0修改成1，如下：

```
/* 修改前 */
Device (SPI1)
        {
            Name (_HID, "PHTY000E")  // _HID: Hardware ID
            Name (_UID, 0)  // _UID: Unique ID
            /* ... */
    	}        
/* 修改后 */
Device (SPI1)
        {
            Name (_HID, "PHYT000E")  // _HID: Hardware ID
            Name (_UID, 1)  // _UID: Unique ID
        	/* ... */
        }
```

### 3.3 `OEM version`更新

​	我们加入新的`DSDT table`时，如果`platform`中已经有一个`DSDT table`，则会去比较两者的`OEM version`，并使用较大版本的表。因此，我们还需要把修改后的`DSDT table`的`OEM version`加大，这样才能用新的表替换旧表，如下：

```
/* 修改前 */
DefinitionBlock ("", "DSDT", 2, "PHYLTD", "PHYTIUM.", 0x00000001)

/* 修改后 */
DefinitionBlock ("", "DSDT", 2, "PHYLTD", "PHYTIUM.", 0x00000002)
```

> `OEM version`的修改也是在`dsdt.dsl`文件中进行。
>
> 笔者并不清楚如果只修改`dsdt.dsl`的设备描述，而不修改其`OEM version`时，最后会出现什么情况。是会启动不了系统，还是报错，还是修改`DSDT table`无效，或是其他什么现象。
>
> 每次更新`DSDT table`时都必须要增大其`OEM version`。

### 3.4 编译修改后的`dsdt.dsl`

```shell
# 解析出dsdt.aml文件
$ iasl -sa dsdt.dsl
```

### 3.5 将`dsdt.aml`加入到`initrd`文件中

```shell
# 创建kernel/firmware/acpi目录
$ mkdir -p kernel/firmware/acpi

$ cp dsdt.aml kernel/firmware/acpi
# 创建acpi_test_initrd文件，一般放到/boot/目录下
$ find kernel | cpio -H newc --create > /boot/acpi_test_initrd
# 新创建的acpi_test_initrd放在前面，之前使用的initrd.img-4.20.17放在其后面
$ cat /boot/initrd.img-4.20.17 >> /boot/acpi_test_initrd
```

### 3.6 重启使用新的`initrd`

​	重启时在`grub`中修改`boot initrd`，如下：

```
/* 修改前 */
initrd /boot/initrd.img-4.20.17

/* 修改后 */
initrd /boot/acpi_test_initrd
```

### 3.7 校验是否生效

​	使用`isal`重新解析出`DSDT.dsl`文件，使用`vim`工具查看是否为修改后的内容。