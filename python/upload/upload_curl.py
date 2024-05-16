from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import cgi


class RequestHandler(BaseHTTPRequestHandler):
    upload_dir = '/path/to/your/upload/directory'  # 请将这里替换为你的目标目录

    def do_POST(self):
        # 解析表单数据
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )

        # 检查表单中是否有文件数据
        if 'file' in form:
            file_item = form['file']
            # 检查是否确实是一个文件
            if file_item.filename:
                # 定义文件的保存路径
                file_path = os.path.join(self.upload_dir, file_item.filename)
                # 确保保存路径存在
                os.makedirs(self.upload_dir, exist_ok=True)

                # 以二进制写入模式打开文件
                with open(file_path, 'wb') as output_file:
                    # file_item.file 是一个文件对象，可以进行读取
                    while True:
                        chunk = file_item.file.read(100000)
                        if not chunk:
                            break
                        output_file.write(chunk)

                # 发送200响应
                self.send_response(200)
                self.end_headers()
                response = f"File '{file_item.filename}' uploaded successfully to '{file_path}'"
                self.wfile.write(response.encode())
            else:
                # 如果不是一个文件，返回400 Bad Request
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"No file was uploaded.")
        else:
            # 如果表单中没有文件数据，返回400 Bad Request
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing file in form data.")


def run(server_class=HTTPServer, handler_class=RequestHandler, port=8006):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()


if __name__ == "__main__":
    run()
    #curl -F "file=@/path/to/your/file.tar" http://x.x.x.x:8006
