#!/usr/bin/env bash
set -euo pipefail

# 需要 root 执行。默认只部署 Kubernetes，不安装 KubeSphere。

K8S_VERSION="v1.31.11"
TARGET_ARCH=""
KKZONE_VALUE="${KKZONE:-global}"
PURGE_DOCKER="false"

usage() {
  cat <<EOF
Usage: $0 [--k8s-version v1.31.11] [--arch amd64|arm64] [--kkzone global|cn] [--purge-docker]
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

DOWNLOAD_ARCH="${TARGET_ARCH:-${HOST_ARCH}}"
for binary in kubeadm kubectl kubelet; do
  K8S_BINARY_URL="https://dl.k8s.io/release/${K8S_VERSION}/bin/linux/${DOWNLOAD_ARCH}/${binary}"
  if ! curl -fsI "${K8S_BINARY_URL}" >/dev/null 2>&1; then
    cat >&2 <<EOF
Kubernetes binary not found: ${K8S_BINARY_URL}
Please choose an existing Kubernetes patch version for ${DOWNLOAD_ARCH}.
For Kubernetes 1.31, v1.31.11 is the default for this script.
EOF
    exit 1
  fi
done

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
  CREATE_ARGS+=(--yes)
fi

run_create_cluster() {
  if printf '%s\n' "${CREATE_ARGS[@]}" | grep -qx -- "--yes"; then
    ./kk "${CREATE_ARGS[@]}"
  else
    printf 'yes\n' | ./kk "${CREATE_ARGS[@]}"
  fi
}

ingress_nginx_version_for_k8s() {
  local kube_version="$1"
  local minor

  minor="$(printf '%s\n' "${kube_version}" | sed -E 's/^v?1\.([0-9]+)\..*/\1/')"
  # Based on the official ingress-nginx supported versions table.
  case "${minor}" in
    23) printf '%s\n' "v1.6.4" ;;
    24) printf '%s\n' "v1.8.4" ;;
    25) printf '%s\n' "v1.9.6" ;;
    26|27) printf '%s\n' "v1.11.8" ;;
    28) printf '%s\n' "v1.12.1" ;;
    29) printf '%s\n' "v1.13.9" ;;
    30) printf '%s\n' "v1.14.5" ;;
    31|32|33|34) printf '%s\n' "v1.15.1" ;;
    *)
      echo "No ingress-nginx version mapping for Kubernetes ${kube_version}." >&2
      return 1
      ;;
  esac
}

install_ingress_nginx() {
  local kube_version="$1"
  local ingress_version manifest_url

  ingress_version="$(ingress_nginx_version_for_k8s "${kube_version}")"
  manifest_url="https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-${ingress_version}/deploy/static/provider/cloud/deploy.yaml"

  echo "Installing ingress-nginx ${ingress_version} for Kubernetes ${kube_version}"
  kubectl apply -f "${manifest_url}"
  kubectl -n ingress-nginx patch service ingress-nginx-controller -p '{"spec":{"type":"NodePort"}}'
  kubectl -n ingress-nginx rollout status deployment/ingress-nginx-controller --timeout=300s
  kubectl get ingressclass
  kubectl -n ingress-nginx get pods -o wide
  kubectl -n ingress-nginx get service ingress-nginx-controller -o wide
}

download_kubekey_artifact() {
  local target_path="$1"
  local url="$2"
  local executable="${3:-false}"

  if [[ -f "${target_path}" ]]; then
    return 0
  fi

  mkdir -p "$(dirname "${target_path}")"
  echo "Preloading KubeKey artifact: ${url}"
  curl -fL --retry 3 --retry-delay 2 -o "${target_path}" "${url}"

  if [[ "${executable}" == "true" ]]; then
    chmod +x "${target_path}"
  fi
}

preload_common_kubekey_artifacts() {
  local arch="$1"
  local kube_version="$2"
  local kube_version_number="${kube_version#v}"
  local cache_root="${PWD}/kubekey/kubekey"
  local binary

  download_kubekey_artifact \
    "${cache_root}/etcd/v3.5.24/${arch}/etcd-v3.5.24-linux-${arch}.tar.gz" \
    "https://github.com/etcd-io/etcd/releases/download/v3.5.24/etcd-v3.5.24-linux-${arch}.tar.gz"
  download_kubekey_artifact \
    "${cache_root}/crictl/v1.31.0/${arch}/crictl-v1.31.0-linux-${arch}.tar.gz" \
    "https://github.com/kubernetes-sigs/cri-tools/releases/download/v1.31.0/crictl-v1.31.0-linux-${arch}.tar.gz"
  download_kubekey_artifact \
    "${cache_root}/runc/v1.1.12/${arch}/runc.${arch}" \
    "https://github.com/opencontainers/runc/releases/download/v1.1.12/runc.${arch}" \
    true
  download_kubekey_artifact \
    "${cache_root}/containerd/v1.7.13/${arch}/containerd-1.7.13-linux-${arch}.tar.gz" \
    "https://github.com/containerd/containerd/releases/download/v1.7.13/containerd-1.7.13-linux-${arch}.tar.gz"
  download_kubekey_artifact \
    "${cache_root}/helm/v3.13.3/${arch}/helm-v3.13.3-linux-${arch}.tar.gz" \
    "https://get.helm.sh/helm-v3.13.3-linux-${arch}.tar.gz"
  download_kubekey_artifact \
    "${cache_root}/cni/plugins/v1.9.1/${arch}/cni-plugins-linux-${arch}-v1.9.1.tgz" \
    "https://github.com/containernetworking/plugins/releases/download/v1.9.1/cni-plugins-linux-${arch}-v1.9.1.tgz"
  download_kubekey_artifact \
    "${cache_root}/cni/calico/v3.30.5/${arch}/calicoctl-linux-${arch}" \
    "https://github.com/projectcalico/calico/releases/download/v3.30.5/calicoctl-linux-${arch}" \
    true

  for binary in kubeadm kubectl kubelet; do
    download_kubekey_artifact \
      "${cache_root}/kube/v${kube_version_number}/${arch}/${binary}" \
      "https://dl.k8s.io/release/v${kube_version_number}/bin/linux/${arch}/${binary}" \
      true
  done
}

fetch_missing_kubekey_artifacts() {
  local log_file="$1"
  local fetched=0
  local missing_path

  while IFS= read -r missing_path; do
    local file_name version component version_number artifact_arch url

    missing_path="${missing_path%:}"
    file_name="$(basename "${missing_path}")"
    component="$(printf '%s\n' "${missing_path}" | sed -E 's#.*/kubekey/([^/]+)/.*#\1#')"
    version="$(printf '%s\n' "${missing_path}" | sed -E 's#.*/kubekey/[^/]+/(plugins/|calico/)?(v?[0-9]+\.[0-9]+\.[0-9]+)/.*#\2#')"
    version_number="${version#v}"
    artifact_arch="$(printf '%s\n' "${missing_path}" | sed -E 's#.*/kubekey/[^/]+/(plugins/|calico/)?v?[0-9]+\.[0-9]+\.[0-9]+/(amd64|arm64)/.*#\2#')"

    case "${component}" in
      etcd)
        url="https://github.com/etcd-io/etcd/releases/download/v${version_number}/${file_name}"
        ;;
      crictl)
        url="https://github.com/kubernetes-sigs/cri-tools/releases/download/v${version_number}/${file_name}"
        ;;
      runc)
        url="https://github.com/opencontainers/runc/releases/download/v${version_number}/${file_name}"
        ;;
      containerd)
        url="https://github.com/containerd/containerd/releases/download/v${version_number}/${file_name}"
        ;;
      cni)
        if [[ "${file_name}" == calicoctl-* ]]; then
          url="https://github.com/projectcalico/calico/releases/download/v${version_number}/${file_name}"
        else
          url="https://github.com/containernetworking/plugins/releases/download/v${version_number}/${file_name}"
        fi
        ;;
      helm)
        url="https://get.helm.sh/${file_name}"
        ;;
      kube)
        url="https://dl.k8s.io/release/v${version_number}/bin/linux/${artifact_arch}/${file_name}"
        ;;
      *)
        echo "Unsupported missing KubeKey artifact: ${missing_path}" >&2
        return 1
        ;;
    esac

    mkdir -p "$(dirname "${missing_path}")"
    echo "Downloading missing KubeKey artifact: ${url}"
    curl -fL --retry 3 --retry-delay 2 -o "${missing_path}" "${url}"
    if [[ "${component}" == "kube" || "${component}" == "runc" || "${file_name}" == calicoctl-* ]]; then
      chmod +x "${missing_path}"
    fi
    fetched=1
  done < <(
    {
      grep -Eo '/[^[:space:]":]+/kubekey/(etcd|crictl|containerd|cni|helm|kube)/v?[0-9]+\.[0-9]+\.[0-9]+/(amd64|arm64)/[^[:space:]":]+' "${log_file}" || true
      grep -Eo '/[^[:space:]":]+/kubekey/cni/plugins/v?[0-9]+\.[0-9]+\.[0-9]+/(amd64|arm64)/[^[:space:]":]+' "${log_file}" || true
      grep -Eo '/[^[:space:]":]+/kubekey/cni/calico/v?[0-9]+\.[0-9]+\.[0-9]+/(amd64|arm64)/[^[:space:]":]+' "${log_file}" || true
      grep -Eo '/[^[:space:]]+/kubekey/runc/v?[0-9]+\.[0-9]+\.[0-9]+/(amd64|arm64)/runc\.(amd64|arm64)' "${log_file}" || true
    } | sort -u
  )

  [[ "${fetched}" == "1" ]]
}

preload_common_kubekey_artifacts "${DOWNLOAD_ARCH}" "${K8S_VERSION}"

for attempt in 1 2 3 4 5 6 7 8 9 10 11 12; do
  CREATE_LOG="$(mktemp)"
  if run_create_cluster 2>&1 | tee "${CREATE_LOG}"; then
    install_ingress_nginx "${K8S_VERSION}"
    exit 0
  fi

  if fetch_missing_kubekey_artifacts "${CREATE_LOG}"; then
    echo "Retrying KubeKey cluster creation after downloading missing artifacts. attempt=${attempt}"
    continue
  fi

  exit 1
done

echo "KubeKey cluster creation still failed after retrying missing artifacts." >&2
exit 1
