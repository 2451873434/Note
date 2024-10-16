# IO性能压测工具——FIO

> 参考链接：
>
> [fio使用指南](https://blog.csdn.net/sch0120/article/details/76154205)

以下是对`fio-2.0.9 HOWTO`文档的翻译，fio参数太多了，翻译该文档是并没有测试每一个参数的功能和使用方法，只有少量参数做了试验，大部分参数采用的是根据字面翻译或是个人理解的翻译，必然有些出入，先发出来，以后又使用的时候再补充和修改。

## 1、简介

fio最初是用来节省为特定负载写专门测试程序，或是进行性能测试，或是找到和重现bug的时间。写这么一个测试应用是非常浪费时间的。因此需要一个工具来模拟给定的io负载，而不用重复的写一个又一个的特定的测试程序。但是test负载很难定义，因为可能会产生很多进程或线程，他们每一个都用他们自己的方式产生IO。fio需要足够灵活来模拟这些case。

## 2、典型的fio的工作过程

1. 写一个job文件来描述要仿真的io负载。一个job文件可以控制产生任意数目的线程和文件。典型的job文件有一个global段（定义共享参数），一个或多个job段（描述具体要产生的job）。
2. 运行时，fio从文件读取这些参数并做处理，根据这些参数描述，启动这些仿真线程/进程。

## 3、运行fio

运行方式如下：

```shell
# fio job_file
```

它会根据`job_file`的内容来运行。你可以在命令行中指定多个`job_file`，`fio`进串行化运行这些文件。相当于在同一个`job file`不同的`section`之间使用了`stonewall`参数。

如果某个`job_file`中只包含一个`job`，那么可以在命令行中给出参数来直接运行，不再需要读取`job_file`。命令行参数同`job_file`参数的格式是一样的。比如，在`job_file`中的参数`iodepth=2`，在命令行中可以写成`-iodepth 2`或是`-iodepth=2`。

`fio`不需要使用`root`权限支持，除非使用到的文件或设备需要`root`权限。一些选项可能会被限制，比如内存锁、`io`调度器切换或是`nice value`降级。

## 4、job文件格式

`job_file`格式采用经典的`ini`文件，`[]`中的值表示`job name`，可以采用任意的ASCII字符，`global`除外，`global`具有特殊的意义。`Global Section`描述了`job_file`中各个`job`的默认配置值。一个`job section`可以覆盖`global section`中的参数，一个`job_file`可以包含几个`global section`，一个job只会受到它上面的`global section`的影响。`;`和`#`可以用作注释。

1. 如下是一个表示两个进程，分别从一个128MB文件中随机读的`job file`：

```ini
# start job file
[global]
rw=randread
size=128m

[job1]

[job2]
# end job file
```

如果用命令写，则是：

```shell
$ fio -name=global -rw=randread -size=128m -name=job1 -name=job2
```

2. 如下是一个表示多个进程随机写文件的实例：

```ini
# start job file
[random-writers]
ioengine=libaio
iodepth=4
rw=randwrite
bs=32k
direct=0
size=64m
numjobs=4
# end job file
```

上述实例表示：采用async，每一个文件的队列长度为4，采用随机写，采用32k的块，采用非direct io，共有4个进程，每个进程随机写64M的文件，也可以采用下面的命令：

```shell
$ fio -name=random-writers -ioengine=libaio -iodepth=4 -rw=randwrite -bs=32k -direct=0 -size=64m -numjobs=4
```

## 5、环境变量

在`job file`中支持环境变量扩展，类似于`${VARNAME}`可以作为选项的值。有如下实例：

```shell
$ SIZE=64m NUMJOBS=4 fio jobfile,fio
# start job file
[random-writers]
rw=randwrite
size=${SIZE}
numjobs=${NUMJOBS}
# end job file
```

`fio`中有一些保留keywords，在内部将其替换成合适的值，这些`keywords`是：

```
$pagesize	当前系统的页的大小
$mb_memory	系统的总内存的大小，以MB为单位
$ncpus		在线有效的cpu数
```

## 6、一个job file包含的基本的参数

### 6.1 IO类型

向文件发起的IO类型。

#### 6.1.1 rw=str

`readwrite=str`，`str`分为以下几种：

| str       | 说明         |
| --------- | ------------ |
| read      | 顺序读       |
| write     | 顺序写       |
| randwrite | 随机写       |
| randread  | 随机读       |
| readwrite | 顺序混合读写 |
| randrw    | 随机混合读写 |

**参数备注**

对于混合io类型，混认是50%的读，50%的写，对于特定的io类型，因为速度可能不同，结果可能会稍有偏差。

通过在str之后加`:<nr>`可以配置在执行一下获取offset操作之前要执行的IO次数。如果后缀用于顺序IO类型的话，那么将在每次IO之后，将这个值加到产生的offset之后。如`rw=write:4k`，每次写之后将会跳过4K。

#### 6.1.2 rw_sequencer=str

如果`rw=<str>`后有offset修饰的话，这个选项可以控制这个数字`<nr>`如何修饰产生的IO offset。可以接收的值如下：

* sequential：产生顺序的offset
* identical：产生相同的offset

**参数备注**：

`sequential`仅用于随机IO。通常情况下，fio在每次IO之后，将会生成一个新的随机IO。如`rw=randread:8`，将会在每8次IO之后执行seek，而不是每次IO之后。顺序IO已经是顺序的，再设置为`sequential`并不会产生任何不同。`identical`会产生同`sequential`相似的行为，只是它会连续产生8次相同的offset，然后生成一个新的offset。

### 6.2 block size

产生的IO单元的大小，可以是一个孤立的值，也可以是一个范围。

#### blocksize=int,bs=int

单次IO的block size默认为4K。如果是单个值的话，将会对读写都生效，如果是用逗号隔开的两个值的话，则前面的值对读有效，后面的值对写有效。

```shell
# 读写均使用4k的块
bs=4k
# 读使用4k的块，写使用8k的块
bs=4k,8k
# 读使用默认的值，写使用8k的块
bs=,8k
```

### 6.3 IO size

将会读写多少数据

#### size=int

这个job IO总共要传输数据的大小。FIO将会执行到所有的数据传输完成，除非设定了运行时间（runtime选项）。FIO将会在job定义的文件中平分这个大小，除非设置了`nrfiles`和`filesize`选项。如果size的值不设置的话，FIO将会使用这个文件或设备的总大小。如果这些文件不存在的话，size选项一定要给出。size的值也可以是一个百分比的数，如`size=20%`，fio将会使用给定的文件或设备的20%的空间。

### 6.4 IO引擎

发起IO的方式

#### ioengine=str

定义job向文件发起IO的方式

| 可选参数     | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| `sync`       | 基本的`read`，`write`，`lseek`用来做定位                     |
| `psync`      | 基本的`pread`，`pwrite`                                      |
| `vsync`      | 基本的`readv`，`writev`                                      |
| `libaio`     | Linux专有的异步IO。Linux仅支持非buffered IO的队列行为        |
| `posixaio`   | `glibc posix`异步IO                                          |
| `solarisaio` | `solaris`独有的异步IO                                        |
| `windowsaio` | windows独有的异步IO                                          |
| `mmap`       | 文件通过内存映射到用户空间，使用`memcpy`写入和读出数据       |
| `splice`     | 使用`splice`和`vmsplice`在用户空间和内核之间传输数据         |
| `syslet-rw`  | 使用`syslet`系统调用来构造普通的read/write异步IO             |
| `sg`         | `SCSI generic sg v3 io`，可以是使用`SG_IO ioctl`来同步，或是目标是一个`sg`字符设备，我们使用read和write执行异步IO |
| `null`       | 不传输任何数据，只是伪装成这样。主要用于训练使用fio，或是基本debug/test的目的 |
| `net`        | 根据给定的`host:port`通过网络传输数据。根据具体的协议，`hostname`，`port`，`listen`，`filename`这些选项将被用来说明建立哪种连接，协议选项将决定哪种协议被使用 |
| `netsplice`  | 像net，但是使用`splic/vmsplice`来映射数据和发送/接收数据     |
| `cpuio`      | 不传输任何数据，但是要根据`cpuload=`和`cpucycle=`选项占用CPU周期，如`cpuload=85`将使用job不做任何的实际IO，但要占用85%的CPU周期。在`SMP`机器上，使用`numjobs=<no_of_cpu>`来获取需要的CPU，因为`cpuload`仅会载入单个CPU，然后占用需要的比例。 |
| `guasi`      | `GUASI IO`引擎是一般的用于异步IO的用户空间异步系统调用接口   |
| `rdma`       | `RDMA IO`引擎支持`RDMA`内存语义（`RDMA_WRITE/RDMA_READ`）和通道主义（`Send/Recv`）用于`InfiniBand`，`RoCE`和`iWARP`协议 |
| `external`   | 指明要调用一个外部的IO引擎（二进制文件）。如`ioenigine=external:/tmp/foo.o`将载入`/tmp`目录下的`foo.o`这个引擎 |

### 6.5 IO depth

如果IO引擎是异步的，这个指定我们需要保持的队列深度

#### iodepth=int

加于文件之上的保持的IO单元。默认对于每个文件来说是1，可以设置一个更大的值来提供并发度。`iodepth`大于1不会影响同步IO引擎（除非`verify_async`这个选项被设置）。即使是异步引擎也可能会施加操作系统限制，导致无法实现所需的深度。这会在Linux使用`libaio`并且设置direct=1的时候发生，因为`buffered io`在OS中不是异步的。在外部通过类似于`iostat`这些工具来观察队列深度来保证这个IO队列深度是我们想要的。

### 6.6 IO type

#### 6.6.1 direct=bool

true，则表明采用non-buffered io，同O_DIRECT效果一样。`ZFS`和`Solaris`不支持`direct io`，在windows同步IO引擎不支持`direct io`。

#### 6.6.2 buffered=bool

true，则表明采用`buffered io`。

### 6.7 Num files

负载将分发到几个文件之中

#### 6.7.1 nrfiles=int

用于这个job的文件数目，默认为1

#### 6.7.2 openfiles=int

在同一时间可以同时打开的文件数目，默认同`nrfiles`相等，可以设置小一些，来限制同时打开的文件数目。

### 6.8 Num threads

#### numjobs=int

创建特定数目的job副本。可能是创建大量的线程/进程来执行同一件事。我们将这样一系列的job，看作一个特定的group。