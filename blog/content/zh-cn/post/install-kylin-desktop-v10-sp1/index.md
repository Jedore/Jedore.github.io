---
title: "VBox安装银河麒麟桌面操作系统 Kylin V10"
description:
date: 2024-05-04T12:15:52+08:00
math: false
image:
license:
hidden: false
comments: false
draft: false
tags:
  - Kylin
categories:
  - 系统
style:
keywords:
---

本地机器: Windows 10

VirtualBox: 7.0.12 r159484 (Qt5.15.2)

### 申请试用

个人用户需要申请才能拿到麒麟操作系统的试用版, 有效期一般1年

https://www.kylinos.cn/support/trial.html

一般申请马上就能通过，会跳到一个试用版下载链接页面
![img0](img0.png)

选择 银河麒麟桌面操作系统V10 AMD64，点击后会出现一个下载页面
![img00](img00.png)
按照提示下载即可， 我这里下载到的是 Kylin-Desktop-V10-SP1-HWE-Release-2303-X86_64.iso

下载后验证一个文件sha256码是否正确, PowerShell 下命令是 `Get-FileHash <file>`

### 创建配置虚拟机

#### 创建

命名
![img1](img1.png)

#### 硬件配置

内存4G, 处理器 2
![img2](img2.png)

#### 虚拟硬盘

50G (如果小于50G,后面系统初始化时需要手动配置硬盘分区，本文未涉及)
![img3](img3.png)
![img4](img4.png)

#### 存储

IDE控制器，选择下载好的iso文件
![img5](img5.png)

#### 显示

Video Memory 选择64M
![img6](img6.png)

#### 网络

适配器1
![img6-1](img6-1.png)
适配器2
![img6-2](img6-2.png)

### 安装

启动虚拟机

#### 检测盘片

使用上下箭头选择 检测盘片， 如果检测失败，后面安装会出问题的
![img8](img8.png)
![img9](img9.png)

#### 安装银河麒麟操作系统

使用上下箭头选择 安装银河麒麟操作系统, 回车执行

![img7](img7.png)

#### 选择中文

![img10](img10.png)

#### 时区设置

![img11](img11.png)

#### 安装途径

![img12](img12.png)

#### 安装方式

要选择中间的硬盘
![img13](img13.png)
格式化磁盘
![img14](img14.png)
按需选择预装软件
![img15](img15.png)

#### 等待安装完成

![img17](img17.png)
安装完成后，重启如下图,输入创建的用户密码即可登录
![img18](img18.png)
登录后，如果网络未连接，点击右下角托盘中的网络图标，选择网络连接即可。

#### 安装增强功能

默认的虚拟机分辨率比较小，窗口很小， 可以通过增强功能增大分辨率.

点击如图 "Insert Guest Additions CD image..."
![img21](img21.png)
打开终端窗口

```bash
cd /media/jedore/VBox_GAs_7.0.12
./VBoxLinuxAdditions.run
```

如下图即成功
![img19](img19.png)
再缩放虚拟机窗口时，分辨率便跟随改变，如下图
![img20](img20.png)

> 更多资料参考
> - [银河麒麟桌面操作系统 V10 产品安装手册](https://gongce.kylinos.cn/static/qilin/res/230803/7e598558100fb09bc1f318d72f0ac65d.pdf)
> - [银河麒麟桌面操作系统V10 常见问题](https://gongce.kylinos.cn/static/img/2024/01/fc4860644d1df11db1f8290b2cd4c2be.pdf)
> - [银河麒麟桌面操作系统V10 产品用户手册](https://gongce.kylinos.cn/static/qilin/res/230803/65653dd8789caf68970e1753fefeafa3.pdf)