#!/bin/bash

git clone https://github.com/lwj-st/kubesphere-install.git
cd kubesphere-install

export KKZONE=cn
echo yes|./kk create cluster --with-kubernetes v1.21.5  --with-kubesphere v3.3.2
