#!/bin/bash
set -e

docker pull registry.cn-hangzhou.aliyuncs.com/kubesphere-tmp/ks-apiserver:v3.3.2
docker pull registry.cn-hangzhou.aliyuncs.com/kubesphere-tmp/ks-console:v3.3.2
docker pull registry.cn-hangzhou.aliyuncs.com/kubesphere-tmp/ks-controller-manager:v3.3.2
docker tag registry.cn-hangzhou.aliyuncs.com/kubesphere-tmp/ks-apiserver:v3.3.2  kubesphere/ks-apiserver:v3.3.2
docker tag registry.cn-hangzhou.aliyuncs.com/kubesphere-tmp/ks-console:v3.3.2 kubesphere/ks-console:v3.3.2
docker tag registry.cn-hangzhou.aliyuncs.com/kubesphere-tmp/ks-controller-manager:v3.3.2 kubesphere/ks-controller-manager:v3.3.2

apt update
apt install socat conntrack -y

export KKZONE=cn
curl -sfL https://get-kk.kubesphere.io | VERSION=v3.0.7 sh -
echo yes|./kk create cluster --with-kubernetes v1.21.5
git clone https://github.com/lwj-st/kubesphere-install.git
cd kubesphere-install
mkdir -p /mnt/prometheus
chmod 777 /mnt/prometheus

kubectl apply -f storage-class.yaml
kubectl apply -f kubesphere-installer.yaml 
kubectl apply -f cluster-configuration.yaml