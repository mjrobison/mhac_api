# SPDX-FileCopyrightText: 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import json
import ssl
import socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from rpc import RpcServer
import websocket
import json
import requests

mqtt_client = None
mqtt_connected = False
last_mqtt_messages = {}

response = requests.get('https://api.mhacsports.com/websocketUrl')
url = dict(response.json())['webSocketUrl']
print(url)
try:
    ws = websocket.WebSocket()
    ws.connect(url)
    server_hello = json.loads(ws.recv())
except Exception as exc:
    print(str(exc))

payload = {
    "op":1,
    "d":{
        "rpcVersion": 1,
        "eventSubscriptions": 0
    },
}
response = ws.send(json.dumps(payload))


# For program flow purposes, we do not want these functions to be called remotely
PROTECTED_FUNCTIONS = ["main", "handle_rpc"]

def connect(mqtt_client, userdata, flags, rc):
    global mqtt_connected
    mqtt_connected = True

def disconnect(mqtt_client, userdata, rc):
    global mqtt_connected
    mqtt_connected = False

def message(client, topic, message):
    last_mqtt_messages[topic] = message

def publish(t, client, topic, message):
    print(t, client, topic, message)
    last_mqtt_messages[topic] = message

class MqttError(Exception):
    """For MQTT Specific Errors"""
    pass

# Default to 1883 as SSL on CPython is not currently supported
def mqtt_init(broker, port=1883, username=None, password=None):
    global mqtt_client, mqtt_connect_info
    mqtt_client = MQTT.MQTT(
        broker=broker,
        port=port,
        username=username,
        password=password,
        socket_pool=socket,
        ssl_context=ssl.create_default_context(),
    )

    mqtt_client.on_connect = connect
    mqtt_client.on_disconnect = disconnect
    mqtt_client.on_message = message
    # mqtt_client.on_publish = publish

def mqtt_connect():
    # mqtt_client.connect()
    print("connected")

def mqtt_publish(topic, payload):
    if mqtt_client is None:
        raise MqttError("MQTT is not initialized")
    try:
        return_val = ''
        hello(payload)
        # last_mqtt_messages[topic] = payload
        # return_val = mqtt_client.publish(topic, json.dumps(payload))
    except BrokenPipeError:
        time.sleep(0.5)
        # mqtt_client.connect()
        return_val = mqtt_client.publish(topic, json.dumps(payload))
    return return_val

def mqtt_subscribe(topic):
    # if mqtt_client is None:
    #     raise MqttError("MQTT is not initialized")
    # return mqtt_client.subscribe(topic)
    return ''

def mqtt_get_last_value(topic):
    """Return the last value we have received regarding a topic"""
    if topic in last_mqtt_messages.keys():
        # return last_mqtt_messages[topic]
        return ''
    return ''

def is_running():
    return True

def handle_rpc(packet):
    """This function will verify good data in packet,
    call the method with parameters, and generate a response
    packet as the return value"""
    # print("Received packet")
    func_name = packet['function']
    if func_name in PROTECTED_FUNCTIONS:
        return rpc.create_response_packet(error=True, message=f"{func_name}'() is a protected function and can not be called.")
    if func_name not in globals():
        return rpc.create_response_packet(error=True, message=f"Function {func_name}() not found")
    try:
        return_val = globals()[func_name](*packet['args'], **packet['kwargs'])
    except MqttError as err:
        return rpc.create_response_packet(error=True, error_type="MQTT", message=str(err))

    packet = rpc.create_response_packet(return_val=return_val)
    return packet

def hello(message):
    # message = json.loads(message)
    print(f"Hello: {message}, {type(message)}")
    action_dict = {
        0: {"action": "incrementHome","value": 1},
        1: {"action": "incrementHome","value": -1},
        2: {"action": "incrementAway","value": 1},
        3: {"action": "incrementHome","value": 2},
        4: {"action": "incrementAway","value": -1},
        5: {"action": "incrementAway","value": 2},
        6: {"action": "incrementHome","value": 3},
        8: {"action": "incrementAway","value": 3},
        9: 'Next Up',
        10: {"action": "incrementPeriod","value": 1},
        11: {"action": "toggleClock","value": True}
    }
    key_number = message.get('key_number', None)

    if key_number is not None:
        if action_dict.get(key_number, None):
            if key_number == 9:
                print(key_number)
                request_payload = {
                    "op": 6,
                    "d": {"eventType": "SetCurrentSceneTransition", "requestId": 0, "requestData": {"TriggerStudioModeTransition" }},
                }
            else: 
               
                request_payload = {
                    "op": 6,
                    "d": {"requestType": "BroadcastCustomEvent", "requestId": 0, "requestData": {"eventData":action_dict[key_number]}},
                }
                
            print(json.dumps(request_payload))
            ws.send(json.dumps(request_payload))


def main():
    """Command line, entry point"""
    global mqtt_connected
    while True:
        rpc.loop(0.25)
        if mqtt_connected and mqtt_client is not None:
            try:
                mqtt_client.loop(0.05)
            except AttributeError:
                mqtt_connected = False

if __name__ == '__main__':
    rpc = RpcServer(handle_rpc)
    try:
        print(f"Listening for RPC Calls, to stop press \"CTRL+C\"")
        main()
    except KeyboardInterrupt:
        print("")
        print(f"Caught interrupt, exiting...")
    rpc.close_serial()
    ws.close()