import  socket
import  threading
import  json

from    dataclasses import dataclass
from    dataclasses import field

@dataclass
class Auschwitz: # sob nigga
    host    :     str  = "127.0.0.1"  
    port    :     int  = 5001
    clients :     list = field(default_factory=list, init=False)
    
    
    def broadcast(self: Auschwitz, message: str, sender_socket: socket.socket):
        # iterate through every client in the array
        # and broadcast the message to them.
        for client in self.clients:
            # check if the client next in the list
            # is the sender_socket, we dont want to send
            # a message to the person who sent it.
            if client != sender_socket:
                try: # broadcast it toclient
                    client.send(message)
                except:
                    self.clients.remove(client)

    def handle_client(self: Auschwitz, client: socket.socket, address: str):
        # method to handle incoming msgs
        print(f"[+] connection from {address}")

        while True:
            try: # decode the incoming JSON as a string
                self.decoded_string = client.recv(1024).decode('utf-8')
                # check if its vlaid
                if self.decoded_string:
                    print(f'[{address}] [{self.decoded_string}]')
                    # broadcast encoded msg 2 everyone
                    self.broadcast(self.decoded_string.encode('utf-8'), client)
                else:
                    break 
            except:
                break
        print(f'[DISCONNECT] {address}')
        # close socke
        self.clients.remove(client)
        client.close()

    def __post_init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # create server socket
        self.server.bind((self.host, self.port))
        self.server.listen()                                                    # start listening
        # dbg
        print(f"[+] Server Started On {self.host}:{self.port}")
        
        while True:
            client_socket, address = self.server.accept()
            # append the incoming client to the ar
            self.clients.append(client_socket)
            # strart the handler thread
            thread = threading.Thread(target=self.handle_client, args=[client_socket, address])
            thread.daemon = True
            thread.start()
            # dbg
            print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')                    



if __name__ == '__main__':
    Auschwitz()