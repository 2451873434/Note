#### 删除当前分支外的所有分支

```shell
git branch | xargs git branch -D
```

#### 删除未跟踪状态

```shell
# 删除git status中未跟踪的文件(-f)和目录(-d)
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
```

