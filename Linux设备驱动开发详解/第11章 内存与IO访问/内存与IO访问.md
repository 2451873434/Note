# 内存与I/O访问

## 1、CPU与内存、I/O

## 1.1 内存空间与I/O空间

​	在`X86`处理器中存在着`I/O`空间的概念，`I/O`空间是相对于内存空间而言的，它通过特定的指令`in`、`out`来访问。端口号标识了外设的寄存器地址。`Intel`语法中的`in`、`out`指令格式如下：

```c
IN 累加器, {端口号|DX}
OUT {端口号|DX}, 累加器
```

​	目前，大多数嵌入式微控制器（如`ARM`、`PowerPC`等）中并不提供`I/O`空间，而仅存在内存空间。内存空间可以直接通过地址、指针来访问，程序及在程序运行中使用的变量和其他数据都存在于内存空间中。

​	内存地址可以直接由`C`语言指针操作，例如在`186`处理器中执行如下代码：

```c
unsigned char *p = (unsigned char *)0xF000FF00;
*p=11;
```

​	以上程序的意义是在绝对地址`0xFFF00`（`186`处理器使用16位段地址和16位偏移地址）中写入11。

​	而在`ARM`、`PowerPC`等未采用段地址的处理器中，`p`指向的内存空间就是`0xF000FF00`，而`*p=11`就是在该地址写入11。

​	再如，`186`处理器启动后会在绝对地址`0xFFFF0`（对应的`C`语言指针是`0xF000FFF0`，`0xF000`为段地址，`0xFFF0`为段内偏移）中执行，代码如下：

```c
typedef void (*lpFunction) ( ); /* 定义一个无参数、无返回类型的函数指针类型 */
lpFunction lpReset = (lpFunction)0xF000FFF0; /* 定义一个函数指针，指向 */
/* CPU启动后所执行的第一条指令的位置 */
lpReset(); /* 调用函数 */
```

​	在以上程序中，没有定义任何一个函数实体，但是程序却执行了这样的函数调用：`lpReset()`，它实际上起到了“软重启”的作用，跳转到`CPU`启动后第一条要执行的指令的位置。因此，可以通过函数指针调用一个没有函数体的“函数”，这本质上只是换一个地址开始执行。

​	即便是在`X86`处理器中，虽然提供了`I/O`空间，如果由我们自己设计电路板，外设仍然可以只挂接在内存空间中。此时，`CPU`可以像访问一个内存单元那样访问外设`I/O`端口，而不需要设立专门的`I/O`指令。因此，内存空间是必需的，而`I/O`空间是可选的。下图给出了内存空间和`I/O`空间的对比。

![](picture/内存空间和IO空间.png)

## 1.2 内存管理单元

​	高性能处理器一般会提供一个内存管理单元（`MMU`），该单元辅助操作系统进行内存管理，提供虚拟地址和物理地址的映射、内存访问权限保护和`Cache`缓存控制等硬件支持。操作系统内核借助`MMU`可以让用户感觉到程序好像可以使用非常大的内存空间，从而使得编程人员在写程序时不用考虑计算机中物理内存的实际容量。

​	为了理解基本的`MMU`操作原理，需先明晰几个概念。

​	1）`TLB`（`Translation Lookaside Buffer`）：即转换旁路缓存，`TLB`是`MMU`的核心部件，它缓存少量的虚拟地址与物理地址的转换关系，是转换表的`Cache`，因此也经常被称为“快表”。

​	2）`TTW`（`Translation Table walk`）：即转换表漫游，当`TLB`中没有缓冲对应的地址转换关系时，需要通过对内存中转换表（大多数处理器的转换表为多级页表，如下图）的访问来获得虚拟地址和物理地址的对应关系。`TTW`成功后，结果应写入`TLB`中。

![](picture/内存中的转换表.png)

​	下图给出了一个典型的`ARM`处理器访问内存的过程，其他处理器也执行类似过程。当`ARM`要访问存储器时，`MMU`先查找`TLB`中的虚拟地址表。如果`ARM`的结构支持分开的数据`TLB`（`DTLB`）和指令`TLB`（`ITLB`），则除了取指令使用`ITLB`外，其他的都使用`DTLB`。`ARM`处理器的`MMU`如下图所示：

![](picture/ARM处理器的MMU.png)

​	若`TLB`中没有虚拟地址的入口，则转换表遍历硬件并从存放于主存储器内的转换表中获取地址转换信息和访问权限（即执行`TTW`），同时将这些信息放入`TLB`，它或者被放在一个没有使用的入口或者替换一个已经存在的入口。之后，在`TLB`条目中控制信息的控制下，当访问权限允许时，对真实物理地址的访问将在`Cache`或者在内存中发生，如下图所示：

![](picture/ARM CPU进行数据访问的流程.png)

​	`ARM`内`TLB`条目中的控制信息用于控制对对应地址的访问权限以及`Cache`的操作。

​	`C`（高速缓存）和`B`（缓冲）位被用来控制对应地址的高速缓存和写缓冲，并决定是否进行高速缓存。

​	访问权限和域位用来控制读写访问是否被允许。如果不允许，`MMU`则向`ARM`处理器发送一个存储器异常，否则访问将被允许进行。

​	上述描述的`MMU`机制针对的虽然是`ARM`处理器，但`PowerPC`、`MIPS`等其他处理器也均有类似的操作。

​	在`Linux 2.6.11`之前，`Linux`内核硬件无关层使用了三级页表`PGD`、`PMD`和`PTE`：从`Linux 2.6.11`开始，为了配合64位`CPU`的体系结构，硬件无关层则使用了4级页表目录管理的方式，即`PGD`、`PUD`、`PMD`和`PTE`。注意这仅仅是一种软件意义上的抽象，实际硬件的页表级数可能少于4。如下代码给出了一个典型的从虚拟地址得到`PTE`的页表查询（`Page Table Walk`）过程，它取自`arch/arm/lib/uaccess_with_memcpy.c`。

```c
static int
pin_page_for_write(const void __user *_addr, pte_t **ptep, spinlock_t **ptlp)
{
	unsigned long addr = (unsigned long)_addr;
	pgd_t *pgd;
	pmd_t *pmd;
	pte_t *pte;
	pud_t *pud;
	spinlock_t *ptl;

	pgd = pgd_offset(current->mm, addr);
	if (unlikely(pgd_none(*pgd) || pgd_bad(*pgd)))
		return 0;

	pud = pud_offset(pgd, addr);
	if (unlikely(pud_none(*pud) || pud_bad(*pud)))
		return 0;

	pmd = pmd_offset(pud, addr);
	if (unlikely(pmd_none(*pmd)))
		return 0;

	/*
	 * A pmd can be bad if it refers to a HugeTLB or THP page.
	 *
	 * Both THP and HugeTLB pages have the same pmd layout
	 * and should not be manipulated by the pte functions.
	 *
	 * Lock the page table for the destination and check
	 * to see that it's still huge and whether or not we will
	 * need to fault on write, or if we have a splitting THP.
	 */
	if (unlikely(pmd_thp_or_huge(*pmd))) {
		ptl = &current->mm->page_table_lock;
		spin_lock(ptl);
		if (unlikely(!pmd_thp_or_huge(*pmd)
                     || pmd_hugewillfault(*pmd)
                     || pmd_trans_splitting(*pmd))) {
			spin_unlock(ptl);
			return 0;
		}

		*ptep = NULL;
		*ptlp = ptl;
		return 1;
	}

	if (unlikely(pmd_bad(*pmd)))
		return 0;

	pte = pte_offset_map_lock(current->mm, pmd, addr, &ptl);
	if (unlikely(!pte_present(*pte) || !pte_young(*pte) ||
                 !pte_write(*pte) || !pte_dirty(*pte))) {
		pte_unmap_unlock(pte, ptl);
		return 0;
	}

	*ptep = pte;
	*ptlp = ptl;

	return 1;
}
```

​	第1行的类型为`struct`，`mm_struct`的参数`mm`用于描述`Linux`进程所占有的内存资源。上述代码中的`pgd_offset`、`pud_offset`、`pmd_offset`分别用于得到一级页表、二级页表和三级页表的入口，最后通过`pte_offset_map_lock`得到目标页表项`pte`。而且第33行还通过`pmd_thp_or_huge()`判断是否有巨页的情况，如果是巨页，就直接访问`pmd`。

​	但是，`MMU`并不是对所有的处理器都是必需的，例如常用的`SAMSUNG`基于`ARM7TDMI`系列的`S3C44B0X`不附带`MMU`，新版的`Linux 2.6`支持不带`MMU`的处理器。在嵌入式系统中，仍存在大量无`MMU`的处理器，`Linux 2.6`为了更广泛地应用于嵌入式系统，融合了`mClinux`，以支持这些无`MMU`系统，如`Dragonball`、`ColdFire`、`Hitachi H8/300`、`Blackfin`等。

# 2、`Linux`内存管理