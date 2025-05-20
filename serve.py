import socket
import json

def load_agent_json(name:str):
    with open(f"human/{name}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return json.dumps(data, ensure_ascii=False)

def start_server(host="127.0.0.1", port=5005):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[Python服务端] 正在监听 {host}:{port}...")

    while True:
        client_socket, addr = server.accept()
        print(f"[连接来自] {addr}")
        try:
            request = client_socket.recv(1024).decode('utf-8')
            print(f"[收到请求] {request}")

            if "GET_AGENT" in request:
                name = request.split(":")[1]  # 提取 name
                agent_data = load_agent_json(name)
                client_socket.sendall(agent_data.encode('utf-8'))
        except Exception as e:
            print("[错误]", e)
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_server()
