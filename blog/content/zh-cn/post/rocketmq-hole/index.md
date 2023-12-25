---
title: "RocketMQ 踩坑记"
description: 最近，公司的一个项目上需要使用消息队列，领导张三拍板使用 RocketMQ , 说是因为 RocketMQ 极致的性能以及丰富的功能, 遂开始调研使用 RocketMQ , 在调研中遇见了一些坑点，记录一下
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

### 环境说明

Rocket 4.8.0 / WSL2(Debian 12.2) / Docker 24.0.7

### 安装 RocketMQ

为了方便，使用 [rocketmq-docker](https://github.com/apache/rocketmq-docker) 以单机的方式部署,
参考 [stage-a-specific-version](https://github.com/apache/rocketmq-docker?tab=readme-ov-file#b-stage-a-specific-version).

<details>
   <summary>1. 下载 rocket-docker </summary>

   ```bash
   $ git clone https://github.com/apache/rocketmq-docker.git
   ```

</details>

<details>
   <summary>2. 生成指定版本的启动模板</summary>

   ```bash
   $ cd rocketmq-docker
   $ sh stage.sh 4.8.0
   $ ls stages/4.8.0/templates/
   data            kubernetes        play-docker-compose.sh  play-docker.sh      play-kubernetes.sh  ssl
   docker-compose  play-consumer.sh  play-docker-dledger.sh  play-docker-tls.sh  play-producer.sh
   ```

</details>

<details>
   <summary>3. 单机模式启动</summary>

   ```bash
   $ cd stages/4.8.0/templates/
   $ ./play-docker.sh centos
   $ docker ps
   CONTAINER ID   IMAGE                   COMMAND                  CREATED          STATUS          PORTS NAMES
   43eecbf367c7   apache/rocketmq:4.8.0   "sh mqbroker -c /hom…"   20 seconds ago   Up 19 seconds   0.0.0.0:10909->10909/tcp, :::10909->10909/tcp, 9876/tcp, 0.0.0.0:10911-10912->10911-10912/tcp, :::10911-10912->10911-10912/tcp   rmqbroker
   445df298e4e5   apache/rocketmq:4.8.0   "sh mqnamesrv"           20 seconds ago   Up 19 seconds   10909/tcp, 0.0.0.0:9876->9876/tcp, :::9876->9876/tcp, 10911-10912/tcp   rmqnamesrv
   ```
   看起来运行正常对吧，但是存在一点问题，稍后再讲。
</details>

### 安装 rocketmq-dashboard

为了方便管理，安装[rocketmq-dashboard](https://github.com/apache/rocketmq-dashboard)， 同样使用 docker 方式。

```bash
$ docker pull apacherocketmq/rocketmq-dashboard:latest
$ docker run -d --name rocketmq-dashboard -e "JAVA_OPTS=-Drocketmq.namesrv.addr=127.0.0.1:9876" -p 8080:8080 -t apacherocketmq/rocketmq-dashboard:latest
```

#### 报错(坑点) 1

打开链接 `http://127.0.0.1:8080` , 会发现弹窗报错，如下:

```text
org.apache.rocketmq.remoting.exception.RemotingConnectException: connect to [127.0.0.1:9876] failed
```

因为 虽然 `rmqnamesrv` 容器服务已经将端口 `9876` 映射到本地(WSL2 Debian), 但是 rocketmq-dashboard 是从容器内部请求9876，故无法成功。

需要将 `JAVA_OPTS=-Drocketmq.namesrv.addr=127.0.0.1:9876` IP 改为 `rmqnamesrv` 容器的 IP。

<details>
   <summary>查看  rmqnamesrv 容器 IP</summary>

```bash
$ docker inspect rmqnamesrv | grep IPAddress
            "SecondaryIPAddresses": null,
            "IPAddress": "172.17.0.2",
                    "IPAddress": "172.17.0.2",
```

</details>

可知 IP 为 `172.17.0.2`。 停止并删除原容器，重新启动。

```bash
$ docker stop rocketmq-dashboard
$ docker rm rocketmq-dashboard
$ docker run -d --name rocketmq-dashboard -e "JAVA_OPTS=-Drocketmq.namesrv.addr=172.17.0.2:9876" -p 8080:8080 -t apacherocketmq/rocketmq-dashboard:latest
```

#### 报错(坑点) 2

再打开链接 `http://127.0.0.1:8080` , 会发现新的弹窗报错，如下:

```text
Caused by: org.apache.rocketmq.remoting.exception.RemotingConnectException: connect to 30.25.90.30:10909 failed
```

这个地址 `30.25.90.30:10909` 其实是 docker 启动 rocketmq 时自带的：

<details>
   <summary>broker.conf 修改前</summary>

   ```bash
   $ cat data/broker/conf/broker.conf
   brokerClusterName = DefaultCluster
   brokerName = broker-abc
   brokerId = 0
   deleteWhen = 04
   fileReservedTime = 48
   brokerRole = ASYNC_MASTER
   flushDiskType = ASYNC_FLUSH
   brokerIP1 = 30.25.90.30
   ```

</details>

在 `broker.conf` 添加一行 `namesrvAddr = 172.17.0.2:9876`
同时更换 `brokerIP1` 的地址(通过`docker inspect rmqbroker | grep IPAddress`命令获取)

<details>
   <summary>broker.conf 修改后</summary>

   ```bash
   $ cat data/broker/conf/broker.conf
   brokerClusterName = DefaultCluster
   brokerName = broker-abc
   brokerId = 0
   deleteWhen = 04
   fileReservedTime = 48
   brokerRole = ASYNC_MASTER
   flushDiskType = ASYNC_FLUSH
   namesrvAddr = 172.17.0.1:9876
   brokerIP1 = 172.17.0.3
   ```

</details>

重启 rocketmq `./play-docker.sh centos`.

再打开链接 `http://127.0.0.1:8080`  即可成功的查看 rocketmq 的各种信息。

*在调研(解决:joy:)完上面的安装问题后, 又遇到了 client sdk 问题。*

### Client SDK (坑点)

RocketMQ官方目前提供了Java/Go/CPP三个比较好的 Client SDK， 我大Python不配了(:angry:)，Python SDK是基于CPP包装的，相当于**阉割
**版，且不支持异步。 但我的项目是使用异步编程的，有大量的磁盘IO、网络IO，俗话说："一处异步，处处异步"~ 但
*rocketmq-client-python* 它不支持异步呀！

卒~~~(:skull_and_crossbones:)

### 写在后面

虽然查看官网文档， 看到了丰富详细的功能介绍，但在安装使用中也遇到了不少坑，虽然也解决了一些，能进行初步的使用。
不过实在不敢继续深入研究和使用，主要怕遇见更多的坑(:running_man:). 而且最重要的是官方没有详细有序的说明(
安装、使用、运维等等)，并且遇到问题一般在官方找不到解决方案!!! 和 Nacos
一样，都是开源出来的看起来功能性能都不错，但是文档、社区等维护的一塌糊涂。好像这两个都是阿里系开源的项目。能接触学习到这两个项目，只能说太年轻~~~

最后，我成功投入了[RabbitMQ](https://www.rabbitmq.com/)的怀抱:grinning:。

