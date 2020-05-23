  
import socket  # Allows us to bind and do all the other basic socket stuff
import errno  # Allows us to handle errors when receiving messages
import sys  # Allows us to exit the program if an error occurs

HEADER_LENGTH = 10  # Our fixed header length
IP = "127.0.0.1"  # IPv4 address of the server
PORT = 1234  # Port Number of the server for this program

my_username = input("Username: ")  # Our username
x = []  # A list for storing the messages to send from our text file

# Make out TCP/IPv4 socket.
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Give the socket the IP and PORT to work with
client_socket.connect((IP, PORT))
# Set connection to non-blocking... Resolved issue of ports being used after socket closes
client_socket.setblocking(False)

# Do bits to the username (encode as utf-8, and other f string bits and pieces)
username = my_username.encode('utf-8')  # Encodes username for transmission
username_header = f"{len(username): <{HEADER_LENGTH}}".encode('utf-8')  # Calculates the message length and encodes it
client_socket.send(username_header + username)
# Sends the server the header of the username, followed by the username itself
# So what happens here is the the server first see the header,
# Which prepares the server for the length of the subsequent string


# Our main loop, which runs until broken out of.
while True:
    # Handle input from client side...
    command = input("Enter what the client should do...")
    # If we enter "report" it will send the entries stored in the corresponding text file
    if "report" in command:
        f = open("entriesB.txt")  # We open the desired text file
        buffer = f.read()  # The contents of the text file is stored in a buffer
        x = buffer.split('\n')  # The file will be split up by new lines, each line will be a message to the server
    # If we enter sick, it will send the sick message to the server to warn other users
    elif "sick" in command:
        buffer = "sick"  # The message we send will simply be sick, the server is prepared for this message
    # Pressing enter will allow the client to be free to receive messages from the server
    else:
        buffer = None  # No message to send, therefore we look to receive

    # If buffer is not empty
    if buffer:
        # Encode the message, same as stuff done to the username, then send
        if buffer == "sick":
            message = f"{len(buffer) :< {HEADER_LENGTH}}" + buffer  # Prepares the header + message
            client_socket.send(bytes(message, "utf-8"))  # We encode and send sick to the server
            print("Infection report sent!")
        else:
            for message in x:  # Send each line from the text file as a message, 1 at a time
                message = f"{len(message) :< {HEADER_LENGTH}}" + message
                client_socket.send(bytes(message, "utf-8"))
            print("Entries sent!")

    # Here is where we receive message from the server itself.
    # The server acts as an intermediary between ourselves and
    # ...Other clients
    try:
        # Here we loop over our received messages, and print them
        while True:
            message_header = client_socket.recv(HEADER_LENGTH)  # We receive the message header from the server
            # This tells us the length of the message to expect to follow the header
            # Nothing received, then server has closed connection
            if not len(message_header):
                print("Connection closed by server")
                sys.exit()

            # Convert the header to an int, then receive and decode rest of string
            message_length = int(message_header.decode("utf-8"))  # The header gives us the message length
            message = client_socket.recv(message_length)  # Using this length we can receive the message
            message = message.decode("utf-8")  # Decode the message into characters

            # print out the message from the server
            print(message)

    except IOError as e:
        # Error in reading data.
        # If we get a different error code than just not reading data
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print("Reading error: {}".format(str(e)))
            sys.exit()
        # We just didn't receive anything
        continue

    except Exception as e:
        # Any other exception - something happened... exit
        print("An error occurred: " .format(str(e)))
        sys.exit()
