---
title: "RocketMQ 踩坑记"
description:
date: 2023-12-20T21:44:51+08:00
math: false
image:
license:
hidden: false
comments: false
draft: false
tags:
  - RocketMQ
categories:
  - 消息队列
style:
---

*最近，公司的一个项目上需要使用消息队列，领导张三拍板使用 RocketMQ , 说是因为 RocketMQ 极致的性能以及丰富的功能, 遂开始调研使用
RocketMQ 。个人常用的调研三件套：**官网文档、安装、使用**, 在调研中遇见了一些坑点，不得不记录一下。*

### 环境说明

Rocket 4.8.0 / WSL2(Debian 12.2) / Docker 24.0.7

### 安装 Install

为了方便，使用 [rocketmq-docker](https://github.com/apache/rocketmq-docker) 以单机的方式部署,
参考 [stage-a-specific-version](https://github.com/apache/rocketmq-docker?tab=readme-ov-file#b-stage-a-specific-version).

1. 下载 rocket-docker
      ```bash
      git clone https://github.com/apache/rocketmq-docker.git
      ```
2. 生成指定版本的启动模板
   ```bash
   cd rocketmq-docker
   sh stage.sh 4.8.0
   
   ```
3. 

### rocketmq-dashboard

### Client SDK
