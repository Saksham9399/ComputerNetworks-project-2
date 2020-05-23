import socket  # Allows us to bind and do all the other basic socket stuff
import select  # Allows us to have multiple users on one server
import math  # We need this to calculate the distance between entries

HEADER_LENGTH = 10  # Our fixed header length
IP = "127.0.0.1"  # IPv4 address
port = 1234  # Port Number

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 and TCP
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Edit socket level options, allows reuse of the same port each time
server_socket.bind((IP, port))  # Binds the address and port to the socket making the server
server_socket.listen()  # Makes our server a listening socket prepared to accept connections.
sockets_List = [server_socket]  # List of sockets
clients = {}  # Dictionary allowing us to find the user-names of clients through their sockets


class Client:  # Our class this will be the objects we will be using to store the data
    def __init__(self, socket, username):  # Each user will have
        self.socket = socket  # 1. Socket - This is basically their address for sending messages
        self.username = username  # 2. A username
        self.entries = []  # 3. A list of their entries, Strings that include their location and time.


class Entry:  # Data for the entry objects
    def __init__(self, longitude, latitude, date, time):
        self.longitude = longitude
        self.latitude = latitude
        self.date = date
        self.time = time


def compare_time(date1, date2, time1, time2):  # Compare time function
    hour1, minute1 = int(time1[:len(time1) // 2]), int(time1[len(time1) // 2:])
    hour2, minute2 = int(time2[:len(time2) // 2]), int(time2[len(time2) // 2:])
    minute1 = minute1 + (hour1 - hour2) * 60
    if abs(date1 - date2) < 1 and abs(minute1 - minute2) < 31:  # Same day, within 30 minutes of each other
        result = True
    else:
        result = False
    return result


def cmp_coords(latA, latB, longA, longB):
    r = 6371  # Radius of earth in km
    dif_lat = math.radians(math.fabs(latB - latA))
    dif_long = math.radians(math.fabs(longB - longA))
    # Calculating the distance between entries
    a1 = math.sin(dif_lat / 2) * math.sin(dif_lat / 2)
    a2 = math.cos(math.radians(latA)) * math.cos(math.radians(latB))
    a3 = math.sin(dif_long / 2) * math.sin(dif_long / 2)
    a = a1 + a2 * a3
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = r * c
    if d < 0.02:
        return True  # If clients are within 20m of each other, return True
    return False


def compare_entries(entry1, entry2):  # Compare the values of the entries as objects
    date1 = int(entry1.date)
    date2 = int(entry2.date)
    time1 = entry1.time
    time2 = entry2.time
    long1 = float(entry1.longitude)
    long2 = float(entry2.longitude)
    lat1 = float(entry1.latitude)
    lat2 = float(entry2.latitude)

    if cmp_coords(lat1, lat2, long1, long2) and compare_time(date1, date2, time1, time2):
        return True  # Return true if our criteria is met
    else:
        return False


def receive_message(socket):  # Method for receiving messages
    try:
        message_header = socket.recv(HEADER_LENGTH)  # Using our header length we can find the length of the message
        if not len(message_header):  # If the message wasn't correctly received we return false
            return False

        message_length = int(message_header.decode("utf-8").strip())  # This finds the length of the message
        data = socket.recv(message_length)  # This receives the message up until the length

        return data.decode('utf-8')  # Returns the message as a string. All messages being received are encoded UTF-8
    except:
        return False  # We return false if no message is received


def send_msg(msg, socket):  # Method for sending messages
    msg_header = f"{len(msg) :< {HEADER_LENGTH}}".encode('utf-8')  # Sets the header as the length of msg and encodes
    msg = msg.encode('utf-8')  # We then encode our message into bits to be transmitted
    socket.send(msg_header + msg)  # We send our header followed by our message
    print(f"Sent warning to {clients[socket].username}!")  # Prints message and destination


def alert_users(sock):  # Method for finding the users that have the same entries as the sick user.
    for entry_sock1 in clients[sock].entries:  # Entries in the sick socket
        for other_socket in sockets_List:  # All the other sockets on the server
            if other_socket != sock and other_socket != server_socket:  # Ignore the sick one and the server
                for entry_sock2 in clients[other_socket].entries:  # Entries in the other clients
                    if compare_entries(entry_sock1, entry_sock2):  # If two entries match send a warning message
                        time = f"{entry_sock2.time[0:2]}:{entry_sock2.time[2:4]}"
                        date = f"{entry_sock2.date[6:8]}/{entry_sock2.date[4:6]}/{entry_sock2.date[0:4]}"
                        message = (f"A user within 20 metres of you at approximately {time} {date} has reported"
                                   f" themselves as Covid-19 positive.\nYou may be at risk of infection, please visit"
                                   f" HSE.ie for more details and try to distance yourself from others.")
                        send_msg(message, other_socket)  # Sends our message to users that could be at risk.
        

while True:  # This is essentially our main loop. This will run forever
    read_sockets, _, exception_sockets = select.select(sockets_List, [], sockets_List)  # This is the confusing part...
    # This line of code waits for network activity and then creates a sub group of active sockets of either readable or exceptional.
    for notified_socket in read_sockets:  # The notified sockets are members of this list with network activity
        if notified_socket == server_socket:  # If its the server that means a new connection is available
            client_socket, client_address = server_socket.accept()  # We accept the new connection
            user = receive_message(client_socket)  # The first message the client sends us is their username

            if user is False:  # If something goes wrong we go back to the start of the loop
                continue

            # If everything goes fine...
            sockets_List.append(client_socket)  # Add the socket to our list of sockets
            clients[client_socket] = Client(client_socket, user)  # Add dictionary entry for the user
            print(f"{user} connected to the server...")  # Print the name of the user.

        else:  # If the notified socket isn't the server it means a client has sent a message
            message = receive_message(notified_socket)  # Receive this incoming message

            if message is False:  # If the message is empty its because the client became notified by disconnecting
                print(f"{clients[notified_socket].username} disconnected from the server...")
                sockets_List.remove(notified_socket)  # We remove them from our lists and dictionary
                del clients[notified_socket]
                continue  # Go back to the start of the loop

            elif message == "sick":  # If the client messages that they're sick then we run our method...
                print(f"Received infection report from {clients[notified_socket].username}")
                alert_users(notified_socket)  # ... for finding users that could be potentially infected

            else:  # If their message isn't sick or empty, we assume its a new entry
                print(f"New entry from {clients[notified_socket].username}: {message}")  # Print the user and entry
                x = message.split(", ")  # Splits message up into different components
                clients[notified_socket].entries.append(Entry(x[0], x[1], x[2], x[3]))  # Adds new entry

    for notified_socket in exception_sockets:  # Sockets in the exceptional sub group have caused an error and need to be removed.
        sockets_List.remove(notified_socket)    # Same as before we remove the users from our lists and dictionary
        del clients[notified_socket]
    # That's everything!