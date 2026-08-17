# `SPI-V2`配置片选超时

**问题现象**

​	在使用`TPM`卡测试`spi-v2`全双工功能时，使用测试脚本测试概率性出现在配置片选时控制器超时的情况，且每次出现时的子脚本均不同，如下为子脚本`TCM2_CC_NV_WriteLock.sh`出现超时的情况。

```shell
$ ./run.sh
......
****************** Running ./TCM2_CC_NV_WriteLock.sh ******************
tpm2_nvdefine -C o -s 32 -P tcwg -g sm3_256 -a "ownerread|policywrite|ownerwrite|writedefine" 1 -T device:/dev/tpm0
echo "foobar" > ../tmp/nv.writelock
tpm2_nvwrite -C o -P tcwg -i ../tmp/nv.writelock 1 -T device:/dev/tpm0
tpm2_nvwritelock -C o -P tcwg 1 -T device:/dev/tpm0
4
tpm2_nvundefine -C o -P tcwg 1 -T device:/dev/tpm0


[ 3053.050774] spi_master spi0: SPI controller timed out
[ 3053.055826] set_cmd16 failed
[ 3053.058705] module:0x   0, cmd:0x0001, sub:0x0007
[ 3053.063401] 0x01 0x00 0x00 0x00
[ 3053.063403] 0x00 0x00 0x00 0x00
[ 3053.066531] 0x00 0x00 0x00 0x00
[ 3053.069661] 0x00 0x00 0x00 0x00
[ 3053.072791] spi_phyt_set_cs:131  enable=0
......
```

​	单独测试子脚本时不会出现超时，重复测试子脚本概率性出现超时。

**问题原因**

​	控制器驱动层触发中断和等待完成中断中间存在部分代码，导致触发中断后，配置片选耗时较短，其完成在等待之前，导致AP侧等待不到完成中断最终超时。

```c
/* 修改前 */
phytium_write_regfile(fts, SPI_REGFILE_AP2RV_INTR_STATE, 0x10);
if (fts->flash_erase == 2)
    ms = 200000;
reinit_completion(&fts->cmd_completion);
ms = wait_for_completion_interruptible_timeout(&fts->cmd_completion, mse
cs_to_jiffies(ms));
```

**解决方法**

```c
/*修改后*/
if (fts->flash_erase == 2)
    ms = 200000;
reinit_completion(&fts->cmd_completion);
phytium_write_regfile(fts, SPI_REGFILE_AP2RV_INTR_STATE, 0x10);
ms = wait_for_completion_interruptible_timeout(&fts->cmd_completion, mse
cs_to_jiffies(ms));
```

