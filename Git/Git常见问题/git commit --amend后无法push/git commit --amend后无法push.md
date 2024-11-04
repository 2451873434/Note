# `git commit --amend`后无法`push`

## 问题现象

​	在做很小的改动时，并不想额外创建一个`commit`，而是使用`git commit --amend`。但是如果你的该`commit`之前就已经被`push`到远程仓库，那么在使用`git commit --amend`之后直接使用`git push`时会报错，如下：

```bash
PS E:\git\Note> git push origin master
To https://gitee.com/pm2451873434/note.git
 ! [rejected]        master -> master (non-fast-forward)
error: failed to push some refs to 'https://gitee.com/pm2451873434/note.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. If you want to integrate the remote changes,
hint: use 'git pull' before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
```

## 解决方法

​	在使用`git push`指令时增加`--force-with-lease`进行强制推送。

```bash
PS E:\git\Note> git push --force-with-lease origin master
Enumerating objects: 246, done.
Counting objects: 100% (246/246), done.
Delta compression using up to 20 threads
Compressing objects: 100% (238/238), done.
Writing objects: 100% (245/245), 8.79 MiB | 4.26 MiB/s, done.
Total 245 (delta 6), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (6/6), done.
remote: Powered by GITEE.COM [1.1.5]
remote: Set trace flag d54dbdac
To https://gitee.com/pm2451873434/note.git
 + ca53619...ef7c94c master -> master (forced update)
```

