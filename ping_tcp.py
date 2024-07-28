"""
    Small utility to Ping your home node and get RSSI & SNR back for antenna testing purposes
    To run : Execute this script with python ping_tcp.py and node name or IP

"""
import logging
import sys
import time
from os import system, name
import meshtastic
import meshtastic.tcp_interface
from pubsub import pub

if len(sys.argv) < 2:
    print(f"Oops!")
    print(f"Usage : ping_tcp.py host IP/name")
    print(f"For example ping_tcp.py 192.168.1.150   or    ping_tcp.py Meshtastic.local")
    sys.exit(1)

node_adr = sys.argv[1]


# General logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='ping_pong.log'
)

   
 
def clear():
    #Clear screen routine
    # for windows
    if name == 'nt':
        _ = system('cls')
 
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


def display_banner():
    banner = """
      //\\
     //  \\esht/\\st/c Ping
    
    Utility to help when antenna testing. The idea is to setup a base station with this script. 
    
    Take your portable node in the field and send a private message to base. You'll receive the 
    RSSI and SNR back. Change antenna and repeat...
     
    """
    print(banner)


def onReceive(packet, interface):
    """called when a packet arrives"""
    #print(f"Received: {packet}")
    
    try:
        if packet['decoded'].get('portnum') == 'TEXT_MESSAGE_APP':
            message = packet['decoded']['payload'].decode('utf-8')
            sender_node_id = packet['fromId']
            sender_id = packet['from']
            to_id = packet.get('to')
            rxRssi = packet['rxRssi']
            rxSnr = packet['rxSnr']
            print(f"Received from: {sender_node_id}, RSSI={rxRssi}, SNR={rxSnr}, Payload={message} \a")
            logging.info(f"Received from: {sender_node_id}, RSSI={rxRssi}, SNR={rxSnr}, Payload={message}")
            if message.__contains__('Ping') and to_id == interface.myInfo.my_node_num:
                tx_message = f"Your signal : RSSI= {rxRssi}, SNR= {rxSnr}"
                #logging.info(f"Sending : {tx_message}")
                print(f"   Ping received, sending " + tx_message)
                Send_Message(tx_message,sender_id, interface)
  
    except KeyError:
        pass  # Ignore KeyError silently
    except UnicodeDecodeError:
        pass  # Ignore UnicodeDecodeError silently


def onConnection(interface, topic=pub.AUTO_TOPIC):  
    """
    Callback function called when we (re)connect to the radio.
    """
    #whoami = iface.myInfo.my_node_num
    #print(f"Connected to Meshtastic device at ")
    
    whoami = interface.myInfo.my_node_num
    print(f"Connected to Meshtastic device {whoami}")
   # print(f"test = {interface.myInfo.my_node_shortName}")



def Send_Message(message, destination, interface):
    max_payload_size = 200
    for i in range(0, len(message), max_payload_size):
        chunk = message[i:i + max_payload_size]
        interface.sendText(
            text=chunk,
            destinationId=destination,
            wantAck=False,
            wantResponse=False
        )
        time.sleep(2)


def main():
    clear()
    display_banner()
    
    print(f"Ping starting using node : {node_adr}")

    pub.subscribe(onReceive, "meshtastic.receive")
    pub.subscribe(onConnection, "meshtastic.connection.established")

    try:
        iface = meshtastic.tcp_interface.TCPInterface(hostname=node_adr)
        print("TCP Interface setup for listening.")
       # while True:
            #time.sleep(10)
        #iface.close()
    except Exception as ex:
        print(f"Error: Could not connect to {node_adr} {ex}")
        sys.exit(1)


 # Keep the script running to listen for messages
    try:
        while True:
            sys.stdout.flush()
            time.sleep(1)  # Sleep to reduce CPU usage
    except KeyboardInterrupt:
        print("Script terminated by user")
        iface.close()

if __name__ == "__main__":
    main()


