#!/usr/bin/env bash
set -euo pipefail

# 需要 root 执行。默认只部署 Kubernetes，不安装 KubeSphere。

K8S_VERSION="v1.31.11"
TARGET_ARCH=""
KKZONE_VALUE="${KKZONE:-cn}"
PURGE_DOCKER="false"

usage() {
  cat <<EOF
Usage: $0 [--k8s-version v1.31.11] [--arch amd64|arm64] [--kkzone cn|global] [--purge-docker]
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --k8s-version)
      K8S_VERSION="${2:?missing value for --k8s-version}"
      shift 2
      ;;
    --arch)
      TARGET_ARCH="${2:?missing value for --arch}"
      shift 2
      ;;
    --kkzone)
      KKZONE_VALUE="${2:?missing value for --kkzone}"
      shift 2
      ;;
    --purge-docker)
      PURGE_DOCKER="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run as root." >&2
  exit 1
fi

case "${K8S_VERSION}" in
  v*) ;;
  *) K8S_VERSION="v${K8S_VERSION}" ;;
esac

case "${TARGET_ARCH}" in
  ""|amd64|arm64) ;;
  x64|x86_64) TARGET_ARCH="amd64" ;;
  aarch64) TARGET_ARCH="arm64" ;;
  *)
    echo "Unsupported architecture: ${TARGET_ARCH}. Use amd64 or arm64." >&2
    exit 1
    ;;
esac

HOST_ARCH="$(uname -m)"
case "${HOST_ARCH}" in
  x86_64) HOST_ARCH="amd64" ;;
  aarch64|arm64) HOST_ARCH="arm64" ;;
esac

if [[ -n "${TARGET_ARCH}" && "${TARGET_ARCH}" != "${HOST_ARCH}" ]]; then
  echo "Requested architecture ${TARGET_ARCH}, but host architecture is ${HOST_ARCH}." >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y curl socat conntrack ipset ipvsadm

export KKZONE="${KKZONE_VALUE}"
curl -sfL https://get-kk.kubesphere.io | sh -

./kk version --show-supported-k8s || true

swapoff -a || true

for module in overlay br_netfilter; do
  modprobe "${module}" 2>/dev/null || true
done

mkdir -p /etc/modules-load.d /etc/sysctl.d

cat >/etc/modules-load.d/k8s.conf <<EOF
overlay
br_netfilter
EOF

cat >/etc/sysctl.d/99-kubernetes-cri.conf <<EOF
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward = 1
EOF
sysctl --system

if command -v systemctl >/dev/null 2>&1; then
  systemctl stop docker.socket docker.service 2>/dev/null || true
  systemctl disable docker.socket docker.service 2>/dev/null || true
fi

if [[ "${PURGE_DOCKER}" == "true" ]]; then
  apt-get purge -y docker-ce docker-ce-cli docker-buildx-plugin docker-compose-plugin moby-engine moby-cli 2>/dev/null || true
  apt-get autoremove -y
fi

if command -v containerd >/dev/null 2>&1; then
  mkdir -p /etc/containerd
  if [[ -f /etc/containerd/config.toml ]]; then
    cp /etc/containerd/config.toml "/etc/containerd/config.toml.bak.$(date +%Y%m%d%H%M%S)"
  fi
  containerd config default > /etc/containerd/config.toml
  sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
  sed -i 's/disabled_plugins = \["cri"\]/disabled_plugins = []/' /etc/containerd/config.toml
  systemctl restart containerd 2>/dev/null || true
fi

CREATE_ARGS=(create cluster --with-kubernetes "${K8S_VERSION}")
if ./kk create cluster --help | grep -q -- "--container-manager"; then
  CREATE_ARGS+=(--container-manager containerd)
else
  CREATE_ARGS+=(--set cri.container_manager=containerd --set cri.cgroup_driver=systemd)
fi

if ./kk create cluster --help | grep -q -- "--yes"; then
  ./kk "${CREATE_ARGS[@]}" --yes
else
  printf 'yes\n' | ./kk "${CREATE_ARGS[@]}"
fi
