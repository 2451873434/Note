#### 删除当前分支外的所有分支

```shell
git branch | xargs git branch -D
```

#### 删除未跟踪状态

```shell
# 删除git status中未跟踪的文件(-f)和目录(-d)
# 可以用于解决“工作区中下列未跟踪的文件将会因为检出操作而被覆盖”
git clean -df

# 做一次删除预演，查看被删除的文件有哪些
git clean -ndf
```

#### 补丁

```shell
# 创建patch文件
git format-patch [commit id] -n
git format-patch -n
# 检查是否能正常打入patch文件
git apply --check [xxx.patch]
# 打入patch文件
git apply [xxx.patch]

# 强制打入补丁
# 此操作会把不能应用的补丁部分存入同目录的.rej文件
git apply --reject [xxx.patch]
```

#### 查看所有提交

```shell
# 一行的描述显示log信息
git log --oneline <filename> > test.txt

# 显示带diff信息的log信息
git log -p <filename> > test.txt
```

