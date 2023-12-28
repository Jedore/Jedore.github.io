---
title: "K8s搭建"
description: 
date: 2023-12-28T09:30:09+08:00
math: false
image: 
license: 
hidden: false
comments: false
draft: false
tags:
  - k8s
categories:
  - k8s
style:
keywords:
---

#### 环境

- Mac Pro - 10.15.6

- 虚拟机 VBox - 6.1.18
- [CentOS 7](http://mirrors.huaweicloud.com/centos/7.9.2009/isos/x86_64/CentOS-7-x86_64-Minimal-2009.iso)

#### 创建虚拟机

3个 master 节点, 2Cpu/2G内存/8G存储

2个 worker 节点,1Cpu/2G内存/8G存储

可以先创建一个虚拟机，安装后配置好静态IP（Mac 桥接、Win NAT+HostOnly），更新一下软件包

```bash
$ yum -y update
```

安装必备软件/docker/k8s软件后，再克隆出其他虚拟机

#### 安装必备软件包

所有节点

```bash
$ yum -y install wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release lrzsz  openssh-server socat  ipvsadm conntrack bind-utils epel-release libffi-devel libaio-devel libxml2-devel cmake python-devel device-mapper-persistent-data lvm2 yum-utils ntpdate
```

#### 安装 docker-ce

所有节点，配置加速器，开机启动

```bash
# install_docker.sh
# switch to ali yum repo
mv -f /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.backup
wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo

# config yum repo for docker
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

# clean yum cache
yum clean all
yum makecache fast

# uninstall old docker
yum -y remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine

# install docker-ce
yum install -y docker-ce-19.03.9-3.el7
systemctl enable docker	# 开机启动
systemctl start docker
systemctl status docker

# modify docker config
cat > /etc/docker/daemon.json <<EOF
{
	"exec-opts": ["native.cgroupdriver=systemd"],
	"log-driver": "json-file",
	"log-opts": {
   	"max-size": "100m"
  },
	"storage-driver": "overlay2",
	"storage-opts": [
  	"overlay2.override_kernel_check=true"
 	],
	"registry-mirrors": ["https://3jno9dmp.mirror.aliyuncs.com"]	# 加速器
}
EOF
systemctl daemon-reload && systemctl restart docker
```

#### 安装 K8S 软件包

所有节点

```bash
# config yum repo for k8s
cat > /etc/yum.repos.d/kubernetes.repo <<EOF
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
EOF

# clean yum cache
yum clean all
yum makecache fast

yum install -y kubeadm-1.20.4 kubelet-1.20.4 kubectl-1.20.4
```

#### 本地化 docker 仓库

若有需要，可以在某个节点服务器搭建一个本地 docker 仓库，或者集群外的服务器搭建仓库也可

#### 初始化系统环境

1. 编辑 `node_ips.sh`中 master/worker 节点 IP, 虚拟IP
2. 添加主 master 节点的公钥到其他节点
3. 设置 hostname
4. 设置 hosts 文件
5. 关闭防火墙
6. 修改时区、更新时间
7. 关闭 selinux
8. 关闭 swap
9. 开启k8s 网络桥接相关内核配置
10. 设置网桥包经IPTables，core文件生成路径，配置永久生效
11. 开启ipvs，不开启ipvs将会使用iptables，但是效率低，所以官网推荐需要开通ipvs内核

主 master 节点执行：

```bash
./init.sh
```

#### 多master高可用

master 节点个数须为奇数,若多于1个，则执行此操作

安装 keepalived, 每个master节点生成 keepalived.conf 文件，当前 节点 master 为 主 `MASTER`，其他 master 为 `BACKUP`, 主 master 权重为 100， 其他 master 权重递减。

- 修改 网卡名字
- 修改 主 master 节点 hostname

```bash
$ ./init_keepalived.sh
```

查看 keepalived 服务正常、虚拟IP绑定到指定网卡，即成功

#### 主master 节点初始化控制面板

编辑 `kubeadm-config.yaml`中虚拟IP及所有主节点IP

```bash
$ kubeadm init --config=kubeadm-config.yaml
```

成功提示，仔细看提示中的命令：

```bash
Your Kubernetes control-plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

Alternatively, if you are the root user, you can run:

  export KUBECONFIG=/etc/kubernetes/admin.conf

# 部署 pod 网络命令
You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

You can now join any number of control-plane nodes by copying certificate authorities
and service account keys on each node and then running the following as root:

# 多 master 节点会有这个命令,从节点加入集群命令
  kubeadm join 192.168.31.253:6443 --token eqynnt.y6twqsdyv1s9ij4n \
    --discovery-token-ca-cert-hash sha256:1f52468a76209596d411dad1b8b11545b708f5baf9e82fcb18c498880d5baed0 \
    --control-plane

Then you can join any number of worker nodes by running the following on each as root:
# worker 节点加入集群命令
kubeadm join 192.168.31.253:6443 --token eqynnt.y6twqsdyv1s9ij4n \
    --discovery-token-ca-cert-hash sha256:1f52468a76209596d411dad1b8b11545b708f5baf9e82fcb18c498880d5baed0
```

成功后:

-  非 root 用户执行

  ```bash
  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config
  ```

- root 用户执行

  ```bash
  export KUBECONFIG=/etc/kubernetes/admin.conf
  echo KUBECONFIG=/etc/kubernetes/admin.conf >> .bash_profile
  ```

查看节点`kubectl get nodes` 显示 `Not Ready`状态



> 可直接执行 `init_master.sh`

#### 部署 CNI网络

- flannel

  主master节点

  ```bash
  $ kubectl apply -f kube-flannel.yaml
  ```

  安装完稍等一会，`kubectl get nodes` 显示为 `Ready` 状态

#### 从master 节点加入集群

将另外的 master 节点加入集群，先拷贝证书，再加入集群

修改 加入集群的 命令

```bash
$ ./add_master.sh
```

`kubectl get nodes` 查看结果

#### worker 节点加入集群

root 用户执行

修改加入集群的命令

```bash
$ ./add_worker.sh
```

> token 有效期是24小时，过期自动消失
>
> 查看 token `kubeadm token list`
>
> 创建新的 token `kubeadm token create`
>
> 获取获取ca证书 sha256 编码hash值 
>
> ```bash
> openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt | openssl rsa -pubin -outform der 2>/dev/null | openssl dgst -sha256 -hex | sed 's/^.* //'
> ```

success info：

```bash
This node has joined the cluster:
* Certificate signing request was sent to apiserver and a response was received.
* The Kubelet was informed of the new secure connection details.

Run 'kubectl get nodes' on the control-plane to see this node join the cluster.
```



#### 重置 kubeadm

若出错需要重置 master 的  `kubeadm init` or  worker 的`kubeadm join`

```bash
kubeadm reset
# master 节点需要删除以下文件
rm -rf ~/.kube/
rm -rf /etc/kubernetes/
rm -rf /var/lib/kubelet/
rm -rf /var/lib/etcd
rm -rf /var/lib/dockershim
rm -rf /var/run/kubernetes
rm -rf /var/lib/cni
rm -rf /etc/cni/net.d
```

#### 创建访问权限及 token

[creating-sample-user](https://github.com/kubernetes/dashboard/blob/master/docs/user/access-control/creating-sample-user.md)

[Ref2](https://www.cnblogs.com/jackluo/p/12228289.html)

```bash
# dashboard-adminuser.yaml
$ kubectl apply -f dashboard-adminuser.yaml
$ kubectl -n kubernetes-dashboard get secret $(kubectl -n kubernetes-dashboard get sa/admin-user -o jsonpath="{.secrets[0].name}") -o go-template="{{.data.token | base64decode}}"
```



#### Dashboard UI

[Ref](https://kubernetes.io/zh/docs/tasks/access-application-cluster/web-ui-dashboard/)

```bash
# yaml链接需要翻墙
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.2.0/aio/deploy/recommended.yaml
# 或
kubectl apply -f dashboard.yaml
# 查看状态并稍等一会
kubectl get pods --all-namespaces
```

>   可以参考 [github recommended.yaml](https://github.com/kubernetes/dashboard/blob/master/aio/deploy/recommended.yaml)
>
>   recommended.yaml （本地用命 dashboard.yaml ）
>
>   需要两个镜像 其中 `kubernetesui/metrics-scraper:v1.0.6`下载比较慢且阿里源没找到此镜像

此时外部访问不了 dashboard

```bash
# 允许外部访问
kubectl proxy --address='0.0.0.0'  --accept-hosts='^*$'
```

访问 `http://192.168.56.102:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/`, 提示:

```json
{
  "kind": "Status",
  "apiVersion": "v1",
  "metadata": {
    
  },
  "status": "Failure",
  "message": "error trying to reach service: dial tcp 10.244.1.3:8443: i/o timeout",
  "code": 500
}
```

此问题应该是 dashboard 服务或网络服务有问题，删掉 worker 节点，再重新创建 dashboard 服务 即成功 访问，但是填写 token 后登录无反应无报错

方案：

1. 更换 service 类型

   [kubernetes 1.10安装Dashboard输入Token无响应](https://blog.csdn.net/spring_trees/article/details/80825473)

   直接将 `dashboard.yaml` 更改 service 类型为 `NodePort`，将端口映射出来，也不需要 `kubectl proxy` 做端口转发了

   ```yaml
   spec:
     type: NodePort
     ports:
       - port: 443
         targetPort: 8443
         nodePort: 30001
   ```

   删除原来的资源 `kubectl delete -f dashboard.yaml` 

   创建资源 `kubectl apply -f dashboard.yaml`
   
   但是有个问题，需要找到 dashboard 是运行在哪个节点上，再使用节点 IP 访问
   
   ```bash
   $ kubectl get pod --all-namespaces  -o wide
   NAMESPACE              NAME                                         READY   STATUS    RESTARTS   AGE   IP               NODE      NOMINATED NODE   READINESS GATES
   kubernetes-dashboard   kubernetes-dashboard-9f9799597-lxvc6         1/1     Running   0          73m   192.168.31.155      worker0   <none>           <none>
   ```
   
   现在火狐访问 `https://192.168.31.155:30001` 成功，后使用 token 登录成功
   
   

#### 常用命令

```bash
# 查看 kubelet 日志
journalctl -f -u kubelet
# 删除节点
kubectl delete nodes <node_hostname>
```



#### FQA

- Unable to read config path "/etc/kubernetes/manifests": path does not exist, ignoring

  ```bash
  
  ```

- not install cni plugin

  error info:

  ```bash
  Container runtime network not ready: NetworkReady=false reason:NetworkPluginNotReady message:docker: network plugin is not ready: cni config uninitialized
  ```

  部署 flannel，稍等一下查看 `journalctl -f -u kubelet` 不再提示错误信息

- 添加子节点到集群后报错

  ```bash
  Container runtime network not ready: NetworkReady=false reason:NetworkPluginNotReady message:docker: network plugin is not ready: cni config uninitialized
  ```

  修改 cni 配置文件后，稍等一会

  ```bash
  mkdir -p /etc/cni/net.d/
  
  cat <<EOF> /etc/cni/net.d/10-flannel.conf
  {"name":"cbr0","type":"flannel","delegate": {"isDefaultGateway": true}}
  EOF
  mkdir /usr/share/oci-umount/oci-umount.d -p
  mkdir /run/flannel/
  cat <<EOF> /run/flannel/subnet.env
  FLANNEL_NETWORK=172.100.0.0/16
  FLANNEL_SUBNET=172.100.1.0/24
  FLANNEL_MTU=1450
  FLANNEL_IPMASQ=true
  EOF
  
  systemctl enable kubelet && systemctl start kubelet
  ```

- Chrome 访问 非私密链接

  换成 Firefox 可以

- Unit kubelet.service entered failed state

  在 初始化 master 节点之前 `kubeadm init`, kubelet 服务会不断重启

#### 参考

[centos7安装kubernetes k8s 1.18](https://www.cnblogs.com/faberbeta/p/13961125.html)
