import socket, threading

# 用户访问本机地址127.0.0.1:10050则会将数据包自动转发到8.141.58.64:3389端口上 (待验)
# 单向流数据传递
def tcp_mapping_worker(conn_receiver, conn_sender):
    while True:
        try:
            # 接收数据缓存大小
            data = conn_receiver.recv(2048)
        except Exception:
            print("[-] 关闭: 映射请求已关闭.")
            break
        if not data:
            break
        try:
            conn_sender.sendall(data)
        except Exception:
            print("[-] 错误: 发送数据时出错.")
            break
        print("[+] 映射请求: {} ---> 传输到: {} ---> {} bytes"
              .format(conn_receiver.getpeername(), conn_sender.getpeername(), len(data)))
    conn_receiver.close()
    conn_sender.close()
    return


# 端口映射请求处理
def tcp_mapping_request(local_conn, remote_ip, remote_port):
    remote_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        remote_conn.connect((remote_ip, remote_port))
    except Exception:
        local_conn.close()
        print("[x] 错误: 无法连接到 {}:{} 远程服务器".format(remote_ip, remote_port))
        return
    threading.Thread(target=tcp_mapping_worker, args=(local_conn, remote_conn)).start()
    threading.Thread(target=tcp_mapping_worker, args=(remote_conn, local_conn)).start()
    return


if __name__ == "__main__":
    remote_ip = "8.141.58.64"  # 对端地址
    remote_port = 3389  # 对端端口
    local_ip = "0.0.0.0"  # 本机地址
    local_port = 10050  # 本机端口

    local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_server.bind((local_ip, local_port))
    local_server.listen(5)
    print("[*] 本地端口监听 {}:{}".format(local_ip, local_port))
    while True:
        try:
            (local_conn, local_addr) = local_server.accept()
        except Exception:
            local_server.close()
            break
        threading.Thread(target=tcp_mapping_request, args=(local_conn, remote_ip, remote_port)).start()
