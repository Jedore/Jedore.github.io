---
title: "Jenkins + Gitee Page 自动化部署 Hexo"
description:
date: 2023-12-28T09:25:48+08:00
math: false
image:
license:
hidden: false
comments: false
draft: false
tags:
  - Hexo
  - Jenkins
categories:
  - Hexo
style:
keywords:
---

最近接触到 Hexo ，做的很精美，而且小巧灵活，但是每次编写文档都要编译部署，很不方便，于是考虑自动化部署，关于 Hexo
的自动化部署，有两种考虑：

- Github Actions
- Jenkins

但是 Github 国内访问时而让人崩溃~~~，决定还是用 jenkins（*配好后，确实感觉大材小用*）+ Gitee

### Jenkins 安装

[安装Jenkins](https://www.jenkins.io/zh/doc/book/installing/#setup-wizard)

[CentOS7安装Jenkins和卸载](https://blog.csdn.net/qq_34272964/article/details/93474659)

### 配置 Gitee / Jenkins

[Gitee Jenkins插件](https://gitee.com/help/articles/4193#article-header0)

### 服务器安装 Nodejs / Hexo

### 配置构建脚本

```shell
#!/bin/bash
cd <project-directory>
git pull
/usr/share/node-14.16.0/bin/hexo clean
/usr/share/node-14.16.0/bin/hexo g
```

### 注意

开始因为权限等问题 构建脚本 各种报错，尝试以下两种：

- 添加 sudoers

  ```sh
  # /etc/sudoers
  jenkins ALL=(ALL)     NOPASSWD:ALL
  ```

- 将 jenkins 改为正常普通用户

  /etc/passwd 中

  ```sh
   jenkins:x:994:990:Jenkins Automation Server:/var/lib/jenkins:/bin/false
  ```

  改为

  ```sh
  jenkins:x:994:990:Jenkins Automation Server:/var/lib/jenkins:/bin/bash
  ```

最后成功后，复原以上两点，重启服务，仍可构建成功，小小的眼睛，大大的迷惑。

### FQA

- Jenkins build failed

  ```bash
  jenkins ERROR: Couldn't find any revision to build
  ```

  仓库分支填写错误，使用 Jenkins 的默认名称 `*/master`

- Jenkins 2.263.4. Gitee 发出 webhook post 请求时一直报 403

  此时 jenkins 中 和 gitee 的 webhook 密码均为空，填写一个同样的密码，问题解决

- Build 中 git pull 报错 无权限

  ```bash
  [Gitee-Hexo-Wiki] $ /bin/bash /tmp/jenkins1992597988625327670.sh
  Host key verification failed.
  fatal: Could not read from remote repository.
  
  Please make sure you have the correct access rights
  and the repository exists.
  Build step 'Execute shell' marked build as failure
  Finished: FAILURE
  ```

  首先， jenkins 用户生成 ssh 秘钥，秘钥需要拷贝到 Gitee 全局或仓库的秘钥里，需要 jenkins 对仓库的权限

  其次，需要 jenkins 用户需要手动在终端执行第一次访问，输入yes

  ```bash
  bash-4.2$ git pull
  The authenticity of host 'gitee.com (180.97.125.228)' can't be established.
  ECDSA key fingerprint is SHA256:FQGC9Kn/eye1W8icdBgrQp+KkGYoFgbVr17bmjey0Wc.
  ECDSA key fingerprint is MD5:27:e5:d3:f7:2a:9e:eb:6c:93:cd:1f:c1:47:a3:54:b1.
  Are you sure you want to continue connecting (yes/no)? yes
  Warning: Permanently added 'gitee.com,180.97.125.228' (ECDSA) to the list of known hosts.
  Already up-to-date.
  ```

  此时 jenkins 重新 Build git pull 成功

- Build 中 Command not found

  ```bash
  [Gitee-Hexo-Wiki] $ /bin/bash /tmp/jenkins3872904878897798842.sh
  Already up-to-date.
  /tmp/jenkins3872904878897798842.sh: line 5: hexo: command not found
  /tmp/jenkins3872904878897798842.sh: line 6: hexo: command not found
  ```

  因为 jenkins 执行的是 非交互式 shell，不去查看环境变量

  解决方案（2个皆可）：

    - 加载一下环境变量 `source /etc/bashrc; source /etc/profile` 等
    - 直接填写命令的绝对路径

### 参考

[CentOS7安装Jenkins和卸载](https://blog.csdn.net/qq_34272964/article/details/93474659)

[Jenkins + Gitee(码云) 实现代码自动化构建](https://blog.csdn.net/qq_34272964/article/details/93747652)

[Jenkins+Gogs+Hexo实现自动化部署博客](https://www.lwhweb.com/posts/45278/)

