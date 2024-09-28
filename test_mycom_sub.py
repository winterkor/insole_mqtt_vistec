import paho.mqtt.client as mqtt
import time
import numpy as np
import json

# Define the timeout for message reception in seconds
MESSAGE_TIMEOUT = 300
last_message_time =time.time()

# The callback called when a message has been received on a topic that the client subscribes to.
def on_message(client, userdata, message):
    global last_message_time
    last_message_time = time.time() #If we get the message update the last time
    payload = json.loads(message.payload) #Parse the incoming message payload as JSON
    print(payload)

#Function for checking timeout of the message if the message is not sent
def check_timeout():
    global last_message_time
    current_time = time.time()
    if current_time - last_message_time > MESSAGE_TIMEOUT: #Check if the elapsed time exceeds the timeout
        client.disconnect() #Disconnect the client
        print("No messages received for 300 seconds. Stopping the client.")
        return True
    else:
        return False

#Define the MQTT broker's IP address
mqttBroker = "YOUR_MQTT_BROKER_IP"
client = mqtt.Client(client_id="Main", protocol=mqtt.MQTTv311)
client.connect(mqttBroker, 1883) #Connect to a remote broker
client.on_message = on_message #Set the callback function to handle incoming messages

client.subscribe("data/json") #Subscribe to the topic "data/json"

#Loop the process
while True:
    client.loop() #Process network event and dispatch callback(on_message)
    if check_timeout():
        break
