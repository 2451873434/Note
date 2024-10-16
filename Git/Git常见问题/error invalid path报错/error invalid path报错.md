# Git | error invalid path报错

## 问题现象

```bash
PS E:\git> git clone https://gitee.com/phytium_embedded/phytium-linux-kernel.git
Cloning into 'phytium-linux-kernel'...
remote: Enumerating objects: 271000, done.
remote: Counting objects: 100% (271000/271000), done.
remote: Compressing objects: 100% (161750/161750), done.
remote: Total 271000 (delta 160858), reused 217318 (delta 107229), pack-reused 0
Receiving objects: 100% (271000/271000), 331.31 MiB | 9.50 MiB/s, done.
Resolving deltas: 100% (160858/160858), done.
error: invalid path 'drivers/gpu/drm/nouveau/nvkm/subdev/i2c/aux.c'
fatal: unable to checkout working tree
warning: Clone succeeded, but checkout failed.
You can inspect what was checked out with 'git status'
and retry with 'git restore --source=HEAD :/'

PS E:\git\phytium-linux-kernel> git branch -a
* linux-5.10
  remotes/origin/HEAD -> origin/linux-5.10
  remotes/origin/linux-4.19
  remotes/origin/linux-4.19-rt
  remotes/origin/linux-5.10
  remotes/origin/linux-5.10-rt
  remotes/origin/linux-6.6
  remotes/origin/linux-6.6-rt

PS E:\git\phytium-linux-kernel> git checkout remotes/origin/linux-4.19
error: invalid path 'drivers/gpu/drm/nouveau/nvkm/subdev/i2c/aux.c'
error: invalid path 'drivers/gpu/drm/nouveau/nvkm/subdev/i2c/aux.h'
error: invalid path 'include/soc/arc/aux.h'
```

## 原因

​	根据信息可以看出代码clone是成功的，但是checkout的时候出现了错误。原因是不同文件系统下文件属性或策略导致的。在Git文档上找到一个关于NTFS保护机制的配置`core.protectNTFS`如下：

```
If set to true, do not allow checkout of paths that would cause problems with the NTFS filesystem, e.g. conflict with 8.3 “short” names. Defaults to true on Windows, and false elsewhere.
```

​	`Windows`系统下默认值是`true`，也就是说不符合`NTFS`策略的文件不会被签出，设置为`false`后可以关闭保护机制。

## 解决方法

​	使用如下指令将配置`core.protectNTFS`设置为`false`：

```bash
git config core.protectNTFS false
```

