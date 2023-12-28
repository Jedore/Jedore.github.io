---
title: "Sentry私有化部署"
description: 使用官方 gensentry/onpremise 快速部署私有化
date: 2023-12-28T09:10:36+08:00
math: false
image: 
license: 
hidden: false
comments: false
draft: false
tags:
  - Sentry
categories:
  - APM
style:
keywords:
---

> [Self-Hosted Sentry](https://develop.sentry.dev/self-hosted/)
> 
> [getsentry/onpremise](https://github.com/getsentry/onpremise)
> 
> [install docker compose](https://docs.docker.com/compose/install/)

### 环境

- CentOS 7
- Docker 19.03.6+
- Compose 1.24.1+
- 4 CPU Cores
- 8 GB RAM
- 20 GB Free Disk Space

由于 我的docker是 20 版本(部署可能遇到问题)，比较新，降级为旧版本:

```bash
# list versions
$ yum list docker-ce --showduplicates | sort -r

# downgrade to 19.03.15-3.el7
$ yum downgrade --setopt=obsoletes=0 -y docker-ce-19.03.9-3.el7
$ yum downgrade --setopt=obsoletes=0 -y docker-ce-cli-19.03.9-3.el7

# 安装 docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```



### 下载

下载源码 [21.5.1](https://github.com/getsentry/onpremise/archive/refs/tags/21.5.1.tar.gz)

测试 21.6.0/21.6.1 安装失败存在问题

解压 `tar -zxvf onpremise-21.5.1.tar.gz`

### 安装

切换到 root 用户

暂时不更改默认配置，直接启动

```bash
$ cd onpremise-21.5.1
$ ./install.sh
```

> 配置国内docker镜像仓库，安装应该更快

安装过程中会提示是否创建用户，最好此时创建用户，否则启动后创建会有点麻烦

若提示如下则安装成功：

```bash
You're all done! Run the following command to get Sentry running:
  docker-compose up -d
```

### 启动

```bash
$ docker-compose up -d
Starting sentry_onpremise_zookeeper_1            ... done
Starting sentry_onpremise_smtp_1                 ... done
Starting sentry_onpremise_clickhouse_1           ... done
Creating sentry_onpremise_geoipupdate_1          ... done
Starting sentry_onpremise_symbolicator_1         ... done
Starting sentry_onpremise_postgres_1             ... done
Starting sentry_onpremise_memcached_1            ... done
Creating sentry_onpremise_symbolicator-cleanup_1 ... done
Starting sentry_onpremise_redis_1                ... done
Starting sentry_onpremise_kafka_1                ... done
Starting sentry_onpremise_snuba-replacer_1                           ... done
Starting sentry_onpremise_snuba-transactions-consumer_1              ... done
Starting sentry_onpremise_snuba-outcomes-consumer_1                  ... done
Starting sentry_onpremise_snuba-consumer_1                           ... done
Starting sentry_onpremise_snuba-sessions-consumer_1                  ... done
Starting sentry_onpremise_snuba-api_1                                ... done
Starting sentry_onpremise_snuba-subscription-consumer-events_1       ... done
Starting sentry_onpremise_snuba-subscription-consumer-transactions_1 ... done
Creating sentry_onpremise_snuba-cleanup_1                            ... done
Creating sentry_onpremise_snuba-transactions-cleanup_1               ... done
Creating sentry_onpremise_cron_1                                     ... done
Creating sentry_onpremise_subscription-consumer-events_1             ... done
Creating sentry_onpremise_ingest-consumer_1                          ... done
Creating sentry_onpremise_post-process-forwarder_1                   ... done
Creating sentry_onpremise_sentry-cleanup_1                           ... done
Creating sentry_onpremise_worker_1                                   ... done
Creating sentry_onpremise_web_1                                      ... done
Creating sentry_onpremise_subscription-consumer-transactions_1       ... done
Creating sentry_onpremise_relay_1                                    ... done
Creating sentry_onpremise_nginx_1                                    ... done
```



### 创建用户

若刚才安装过程没有创建用户则在服务器使用一下命令创建用户:

```bash
$ docker-compose run --rm web createuser
Creating sentry_onpremise_web_run ... done
06:08:05 [INFO] sentry.plugins.github: apps-not-configured
Email: jedoreee@189.cn
Password: 
Repeat for confirmation: 
Should this user be a superuser? [y/N]: y
Added to organization: sentry
```



### 访问

浏览器访问 `http://ip:9000`

使用创建好的用户登录即可~

### 注册 Relay服务

 [registering-relay-with-sentry](https://docs.sentry.io/product/relay/getting-started/#registering-relay-with-sentry) 

```bash
$ docker-compose restart relay
```



### 配置邮箱

```yaml
# sentry/config.yml
mail.backend: 'smtp'  # Use dummy if you want to disable email entirely
mail.host: 'smtp.126.com'
mail.port: 25
mail.username: '*****'
mail.password: '******'
mail.use-tls: true
# The email address to send on behalf of
mail.from: '*****'
```

```bash
$ docker-compose restart web worker cron
```

在前端进行邮件测试、账户邮件验证、以及SDK异常邮件通知 的测试验证

### 备份、还原

#### 快速备份

- 备份（项目、用户相关数据，无事件数据）

  ```bash
  $ docker-compose run --rm -T -e SENTRY_LOG_LEVEL=CRITICAL web export > backup.json
  ```

- 还原

  `backup.json` 放在 `onpremise-xxx/sentry` 文件夹下

  ```bash
  $ docker-compose run --rm -T web import /etc/sentry/backup.json
  ```

#### 全量备份

参考 docker 官方 [Backup, restore, or migrate data volumes](https://docs.docker.com/storage/volumes/#backup-restore-or-migrate-data-volumes)

可以通过 `docker-compose.yml` 查看sentry的volumes及对应的文件夹

- 全量数据包含的volumes
  - `sentry-data`
  - `sentry-postgres`
  - `sentry-redis`
  - `sentry-zookeeper`
  - `sentry-kafka`
  - `sentry-clickhouse`
  - `sentry-symbolicator`



`$ docker ps` 查看正在运行的容器名称

- 备份

  ```bash
  # 以 sentry-web 为例
  $ docker run --rm --volumes-from sentry_onpremise_web_1 -v $(pwd):/sentry-data ubuntu tar cvf /sentry-data/sentry-data.tar /data
  ```

  容器 `sentry_onpremise_web_1` 对应的 volume 数据会被压缩到当前路径下的 `sentry-data.tar` 文件

- 还原

  在另一个新安装的 sentry 服务中

  - 先停掉服务 web

    ```bash
    $ docker-compose stop sentry_onpremise_web_1
    ```

  - 执行还原命令

    ```bash
    $ docker run --rm --volumes-from sentry_onpremise_web_1 -v $(pwd):/sentry-data ubuntu bash -c "cd /data && tar xvf /sentry-data/sentry-data.tar --strip 1"
    ```

  `ubuntu` 镜像只是生成临时容器用于操作备份及还原的 压缩、解压命令

### 常用命令

```bash
# 查看某个服务日志
$ docker-compose logs web # worker / cron / relay ...
# 查看所有服务日志
$ docker-compose logs
```

### 问题

#### getsentry/snuba:21.5.1 一直在重启

查看日志如下

```bash
$ docker logs --since 30m <contianer id>
2021-06-21 08:18:44,267 New partitions assigned: {Partition(topic=Topic(name='events'), index=0): 92}
2021-06-21 08:18:44,270 Caught OffsetOutOfRange('KafkaError{code=OFFSET_OUT_OF_RANGE,val=1,str="Broker: Offset out of range"}'), shutting down...
Traceback (most recent call last):
  File "/usr/local/bin/snuba", line 33, in <module>
    sys.exit(load_entry_point('snuba', 'console_scripts', 'snuba')())
  File "/usr/local/lib/python3.8/site-packages/click/core.py", line 829, in __call__
    return self.main(*args, **kwargs)
  File "/usr/local/lib/python3.8/site-packages/click/core.py", line 782, in main
    rv = self.invoke(ctx)
  File "/usr/local/lib/python3.8/site-packages/click/core.py", line 1259, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/usr/local/lib/python3.8/site-packages/click/core.py", line 1066, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/usr/local/lib/python3.8/site-packages/click/core.py", line 610, in invoke
    return callback(*args, **kwargs)
  File "/usr/src/snuba/snuba/cli/subscriptions.py", line 233, in subscriptions
    batching_consumer.run()
  File "/usr/src/snuba/snuba/utils/streams/processing/processor.py", line 116, in run
    self._run_once()
  File "/usr/src/snuba/snuba/utils/streams/processing/processor.py", line 146, in _run_once
    self.__message = self.__consumer.poll(timeout=1.0)
  File "/usr/src/snuba/snuba/subscriptions/consumer.py", line 120, in poll
    message = self.__consumer.poll(timeout)
  File "/usr/src/snuba/snuba/utils/streams/synchronized.py", line 217, in poll
    message = self.__consumer.poll(timeout)
  File "/usr/src/snuba/snuba/utils/streams/backends/kafka/__init__.py", line 396, in poll
    raise OffsetOutOfRange(str(error))
snuba.utils.streams.backends.abstract.OffsetOutOfRange: KafkaError{code=OFFSET_OUT_OF_RANGE,val=1,str="Broker: Offset out of range"}
```

重新安装、重启之后问题消失~~~

#### 安装时出现创建IP路由失败

```bash
Creating network "sentry_onpremise_default" with the default driver
Failed to Setup IP tables: Unable to enable SKIP DNAT rule:  (iptables failed: iptables --wait -t nat -I DOCKER -i br-fc7ec16d0ed7 -j RETURN: iptables: No chain/target/match by that name.
```

重启 docker 服务即可

#### relay 连接 web失败

```bash
$ docker-compose logs relay
Attaching to sentry_onpremise_relay_1
relay_1                                     | 2021-06-22T03:53:42Z [rdkafka::client] ERROR: librdkafka: FAIL [thrd:kafka:9092/bootstrap]: kafka:9092/bootstrap: Connect to ipv4#172.18.0.11:9092 failed: Connection refused (after 4ms in state CONNECT)
relay_1                                     | 2021-06-22T03:53:42Z [rdkafka::client] ERROR: librdkafka: Global error: BrokerTransportFailure (Local: Broker transport failure): kafka:9092/bootstrap: Connect to ipv4#172.18.0.11:9092 failed: Connection refused (after 4ms in state CONNECT)
relay_1                                     | 2021-06-22T03:53:42Z [rdkafka::client] ERROR: librdkafka: Global error: AllBrokersDown (Local: All broker connections are down): 1/1 brokers are down
relay_1                                     | 2021-06-22T03:53:42Z [rdkafka::client] ERROR: librdkafka: FAIL [thrd:kafka:9092/bootstrap]: kafka:9092/bootstrap: Connect to ipv4#172.18.0.11:9092 failed: Connection refused (after 0ms in state CONNECT)
relay_1                                     | 2021-06-22T03:53:42Z [rdkafka::client] ERROR: librdkafka: Global error: BrokerTransportFailure (Local: Broker transport failure): kafka:9092/bootstrap: Connect to ipv4#172.18.0.11:9092 failed: Connection refused (after 0ms in state CONNECT)
relay_1                                     | 2021-06-22T03:53:42Z [rdkafka::client] ERROR: librdkafka: Global error: AllBrokersDown (Local: All broker connections are down): 1/1 brokers are down
relay_1                                     | 2021-06-22T03:53:43Z [rdkafka::client] ERROR: librdkafka: FAIL [thrd:kafka:9092/bootstrap]: kafka:9092/bootstrap: Connect to ipv4#172.18.0.11:9092 failed: Connection refused (after 45ms in state CONNECT, 1 identical error(s) suppressed)
relay_1                                     | 2021-06-22T03:53:43Z [rdkafka::client] ERROR: librdkafka: Global error: BrokerTransportFailure (Local: Broker transport failure): kafka:9092/bootstrap: Connect to ipv4#172.18.0.11:9092 failed: Connection refused (after 45ms in state CONNECT, 1 identical error(s) suppressed)
relay_1                                     | 2021-06-22T03:53:43Z [rdkafka::client] ERROR: librdkafka: FAIL [thrd:kafka:9092/bootstrap]: kafka:9092/bootstrap: Connect to ipv4#172.18.0.11:9092 failed: Connection refused (after 53ms in state CONNECT, 1 identical error(s) suppressed)
relay_1                                     | 2021-06-22T03:53:43Z [rdkafka::client] ERROR: librdkafka: Global error: BrokerTransportFailure (Local: Broker transport failure): kafka:9092/bootstrap: Connect to ipv4#172.18.0.11:9092 failed: Connection refused (after 53ms in state CONNECT, 1 identical error(s) suppressed)
relay_1                                     | 2021-06-22T03:53:47Z [relay_server::actors::upstream] ERROR: authentication encountered error: could not send request to upstream
relay_1                                     |   caused by: error sending request for url (http://web:9000/api/0/relays/register/challenge/): operation timed out
```

[relay unable to connect to web:9000 #771](https://github.com/getsentry/onpremise/issues/771)

[fix: Enable experimental reqwest library for relay](https://github.com/getsentry/onpremise/pull/810)

[New errors stuck in relay_server](https://forum.sentry.io/t/new-errors-stuck-in-relay-server/9660)

解决: 第一次启动后，按照 [registering-relay-with-sentry](https://docs.sentry.io/product/relay/getting-started/#registering-relay-with-sentry) 方式注册 relay，过段时间(多久很迷)重启 relay

要变更 relay 日志级别 `relay/config.yml` 才会有如下的 INFO 日志

```bash
$ docker-compose restart relay
Restarting sentry_onpremise_relay_1 ... done
$ docker-compose logs relay
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::actors::upstream] DEBUG: sending register challenge response
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::service] INFO: spawning http server
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::actors::project_redis] INFO: redis project cache started
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::service] INFO:   listening on: http://0.0.0.0:3000/
relay_1                                     | 2021-06-22T06:21:22Z [actix_net::server::server] INFO: Starting 4 workers
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::actors::store] INFO: store forwarder started
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::actors::project_redis] INFO: redis project cache started
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::actors::project_redis] INFO: redis project cache started
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::actors::project_redis] INFO: redis project cache started
relay_1                                     | 2021-06-22T06:21:22Z [actix_net::server::server] INFO: Starting server on 0.0.0.0:3000
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::actors::controller] INFO: relay server starting
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::actors::connector] INFO: metered connector started
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::actors::envelopes] INFO: envelope manager started
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::actors::project_local] INFO: project local cache started
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::actors::project_upstream] INFO: project upstream cache started
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::actors::project_cache] INFO: project cache started
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::actors::relays] INFO: key cache started
relay_1                                     | 2021-06-22T06:21:22Z [relay_server::actors::upstream] INFO: relay successfully registered with upstream

```



#### 邮件 25 端口无法发送邮件

如果是阿里云服务器，默认封禁25端口出口访问 https://help.aliyun.com/knowledge_detail/56130.html

- 更改sentry 使用 465 邮件端口

  sentry 默认支持 tls 25 端口，不建议使用 SSL

  ```yaml
  # sentry/config.yml
  mail.backend: 'smtp'  # Use dummy if you want to disable email entirely
  mail.host: 'smtp.126.com'
  mail.port: 465
  mail.username: '*****'
  mail.password: '******'
  mail.use-tls: false
  mail.use-ssl: true
  # The email address to send on behalf of
  mail.from: '*****'
  ```

  `mail.from` 可以写为 `Dont Reply <do_not_reply@domain.com>` 格式，展示自定义名称

  也可以将 `mail.use-ssl` 放入 `sentry/sentry.conf.py` 中

  ```python
  # sentry/sentry.conf.py
  SENTRY_OPTIONS['mail.use-ssl'] = True
  ```

  

- 申请 解封25端口（不报希望), 或更换服务器厂商



#### 客户端发送事件失败

错误日志如下：

```bash
$ docker-compose logs nginx
nginx_1                                     | 2021/07/06 06:06:26 [error] 7#7: *1191 connect() failed (111: Connection refused) while connecting to upstream, client: 192.168.90.170, server: , request: "POST /api/2/envelope/ HTTP/1.1", upstream: "http://172.18.0.29:3000/api/2/envelope/", host: "192.168.90.170:9000"
```

解决方案一：

```bash
# nginx/nginx.conf
proxy_set_header X-Forwarded-Proto $scheme;
# 替换为
proxy_set_header X-Forwarded-Proto http;
```

若替换为 `https` 则更新资源时出现以下应答问题

```bash
{"detail":"CSRF Failed: Referer checking failed - Referer is insecure while host is secure."}
```

解决方案二：

```bash
# 重启relay/nginx
$ docker-compose restart relay
$ docker-compose restart nginx
```



#### docker 容器中没有vim

```bash
$ apt-get update
$ apt-get install vim
```

