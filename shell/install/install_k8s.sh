#!/bin/bash

#需要root执行

apt update
apt install socat conntrack -y

curl -sfL https://get-kk.kubesphere.io | sh -
export KKZONE=cn

./kk version --show-supported-k8s
echo yes|./kk create cluster --with-kubernetes v1.21.5
