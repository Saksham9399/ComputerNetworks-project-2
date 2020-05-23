# ComputerNetworks-project-2
An application using socket programming in python for contact tracing to fight off COVID-19
Python3 

How to run the program:
1. Run all the clients and server files in this folder.
2. Enter a username for each client to connect them to the server.
3. In each of the client termials, enter the command "report". This will send the entries of the corresponding txt file from the client to the server.
4. When each client has reported its entries to the server choose a client at random and enter the command "sick". This will send a message from that client to the server that they are ill and the server will begin sending messages to other users that could be at risk.
5. In the other clients' terminals simply press the 'enter' key on your keyboard and they will receive messages from the server if there are some to be received. 
6. A message will be printed in the client window after you press 'enter' warning them of an infection if that client has been exposed to the sick user. We determine this if they have been within 20m of the same location at approximately the same time (+- 30mins).

Which clients trigger others:
Client A, if sick, this will trigger client B and D.
Client B will trigger D.
Client C will trigger no-one, and will not be triggered by any
Client D, triggered by A and B
