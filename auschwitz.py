import  socket
import  threading
import  ssl

from    dataclasses import dataclass
from    dataclasses import field

@dataclass
class Auschwitz: # sob nigga
    host    :     str  = "0.0.0.0"  
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
                    msg_bytes = message if isinstance(message, bytes) else message.encode('utf-8')
                    length = len(msg_bytes)
                    client.send(length.to_bytes(4, 'big') + msg_bytes)
                except:
                    self.clients.remove(client)

    def handle_client(self: Auschwitz, client: socket.socket, address: str):
        # method to handle incoming msgs
        print(f"[+] connection from {address}")

        while True:
            try:
                # read 4-byte length prefix
                length_bytes = b''
                while len(length_bytes) < 4:
                    chunk = client.recv(4 - len(length_bytes))
                    if not chunk:
                        break
                    length_bytes += chunk
                
                if len(length_bytes) < 4:
                    break
                    
                msg_length = int.from_bytes(length_bytes, 'big')
                
                # read exact message length
                msg_data = b''
                while len(msg_data) < msg_length:
                    chunk = client.recv(min(4096, msg_length - len(msg_data)))
                    if not chunk:
                        break
                    msg_data += chunk
                
                if len(msg_data) < msg_length:
                    break
                
                self.decoded_string = msg_data.decode('utf-8')
                # check if its valid
                if self.decoded_string:
                    print(f'[{address}] [{self.decoded_string}]')
                    # broadcast encoded msg 2 everyone
                    self.broadcast(self.decoded_string.encode('utf-8'), client)
                else:
                    break
            except:
                break
                
        print(f'[DISCONNECT] {address}')
        # close socket
        self.clients.remove(client)
        client.close()

    def __post_init__(self):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile='server.crt', keyfile='server.key')
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # create server socket
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen()                                                    # start listening
        # dbg
        print(f"[+] Server Started On {self.host}:{self.port}")
        
        while True:
            client_socket, address = self.server.accept()
            secure_socket = context.wrap_socket(client_socket, server_side=True)
            # append the incoming client to the ar
            self.clients.append(secure_socket)
            # strart the handler thread
            thread = threading.Thread(target=self.handle_client, args=[secure_socket, address])
            thread.daemon = True
            thread.start()
            # dbg
            print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')                    



if __name__ == '__main__':
    Auschwitz()
