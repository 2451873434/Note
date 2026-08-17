20260629进展：
1、在联想服务器（10.31.31.188）（！！！有云芯raid卡！！！）上进行测试：
A.所有CPU在ondemand模式下，单独跑ltp测试3min内出现宕机。报错信息为Unable to handle kernel paging request at virtual address 7fff5000001c24b4
B.所有CPU在ondemand模式下，单独跑fio测试10min内出现宕机，报错信息为Unable to handle kernel paging request at virtual address 7fff00ff83f5041c
C.所有CPU在ondemand模式下，ltp和fiio混合测试3min内出现宕机。报错信息为Unable to handle kernel paging request at virtual address 7fff5000001bbb28
D.所有CPU在performance模式下，，ltp和fiio混合测试2h内没有出现宕机。

2、在飞腾服务器（10.31.31.251）（！！！无raid卡！！！）上进行测试：
A.scp将联想服务器的ltp相关文件拷贝到飞腾服务器上，无法直接使用
B.克隆ltp仓库编译安装进行kirk测试，已经编译安装完成，所有CPU在ondemand模式下，跑ltp和fio混合测试，1h没有出现宕机情况

3、在飞腾服务器（10.31.31.251）（！！！博通raid卡！！！）上进行测试：
插上博通raid卡后，系统无法正常启动，卡在选盘<->选内核之间，原因不明。



20260630进展：

1、联达兴机器其他同事在用

2、做以下测试，定位问题是否特定于ondemand的实现：
A.所有CPU在conservative模式下，做kirk（ltp）和fio测试10min出现宕机。
B.所有CPU在schedutil模式下，做kirk（ltp）和fio测试3h内没有出现宕机。
C..所有CPU在powersave模式下，做kirk（ltp）和fio测试1min内出现宕机。

后续计划：
尝试抓取宕机时的cpu的频率切换情况（即宕机时cpu当前频率和目标频率）



20260701进展：
1、抓取宕机时各个CPU的频率切换情况，详见日志文件（搜索“target=”）
由于cpu频率数据采样代码在od_update中，所以cur=0,target=0的cpu表示整个测试过程中cpu频率均未有变化。其它cur和target有数据表示宕机时该cpu的频率是否有变化。

2、测试时发现多数情况宕机处于ltp的fork13测试项处，尝试使用“./kirk --run-command fork13”指令单独测试fork13，有如下情况：
A.所有CPU在performance模式下时，fork13测试项通过
B.所有CPU在ondemand模式下时,fork13测试项失败，但是不会宕机。
查询相关资料看是否能从fork13做切入点进行问题分析

后续计划：
多抓取几次宕机时cpu频率变化的信息并进行分析



20260702进展

使用userspace接口，测试在不同CPU频率下进行ltp和fio测试（CPU最低频率50MHz，最高频率2100MHz），查看是否会宕机，测试情况如下：
A.50MHz，10min内宕机
B.2100MHz，2h内不宕机
C.1600MHz，1h内不宕机
D.800MHz，1h内不宕机
E.400MHz，正在测试
后续计划：
CPU频率步长为50MHz，继续细化CPU频率进行测试



20260703进展：

根据昨天测试结果，推断宕机大概率和CPU所处的频点有关，做了如下几个CPU频率的长时间测试以验证猜想：
1、2100MHz、1600MHz、1000MHz、900MHz，3h内均不宕机
2、800MHz、400MHz、200MHz、100MHz、50MHz，1-10min内出现宕机
备注：昨天测试800MHz下1h不宕机的情况为频点未设置成功，今天复测了800MHz下3次均在10min内宕机
结论：CPU处于800MHz下（含800MHz）会出现宕机，在高于900MHz（含900MHz）时不会宕机

后续计划：
和固件CPU调频的相关的同事沟通分析根因



20260706进展：

1、联想机器上设置ondemand模式，并设置最低频率为900MHz，进行ltp测试2h不宕机
2、联想机器上DVFS_ENABLE为打开状态，飞腾服务器上DVFS_ENABLE为关闭状态
3、联想机器上不同频率对应不同的电压，如下：
			(50~800]MHZ ： 760mv
			(800~1500]MHZ ： 780mv
			(1500~1700]MHZ ： 790 mv
			(1700~1900]MHZ ：800mv
			(1900~ 2000]MHZ  ： 820mv
			(2000~ 2100]MHZ ：840mv
4、飞腾S5000C服务器（不插raid卡），cpu处于ondemand/userspace模式进行ltp需要重新测试（之前出现宕机情况为其他同事使用该服务器的手动关机）（进行中）

后续计划：
1.关闭DVFS，只调频。
2.打开DVFS，将50~800MHZ的对应电压提高到780mv。



20260707进展：
联想机器：
1、关闭DVFS，只调频不调压（默认为上一次关机时的电压，780mv）。设置userspace模式400MHz，进行ltp和fio混合测试，2h未出现宕机。
2、打开DVFS，将50~800MHZ的对应电压提高到780mv。设置userspace模式400MHz，进行ltp和fio混合测试，1h未出现宕机。



20260708进展：

联想机器：做了多次测试以确定问题是否和CPU电压有关。
1、关闭DVFS，只调频不调压。
设置ondemand模式，进行ltp和fio混合测试，2h未宕机
设置userspace模式200MHz，进行ltp和fio混合测试，2h未宕机
2、打开DVFS，将50~800MHZ的对应电压提高到780mv。
设置ondemand模式，进行ltp和fio混合测试，2h未宕机
设置userspace模式200MHz，进行ltp和fio混合测试，2h未宕机

后续计划：
移除联想机器上的raid卡后重新测试，确认宕机问题是否和拔插raid卡相关



频点

10.57.3.81：3