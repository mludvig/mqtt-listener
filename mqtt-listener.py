#!/usr/bin/env python3

# Execute a script upon AWS IoT MQTT message reception
# Author: Michael Ludvig @ https://aws.nz
# Inspired by aws-iot-device-sdk-python/samples/basicPubSub/basicPubSub.py

import os
import logging
import time
import argparse
import json
import subprocess
import configparser

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Custom MQTT message callback
def custom_callback(client, userdata, message):
    logging.info(f"Received a new message from {message.topic}: ")
    logging.info(f"Payload: {message.payload}")
    if params.get('script'):
        logging.debug(f"Executing: {params['script']}")
        env = os.environ.copy()
        env['MQTT_PAYLOAD'] = message.payload
        env['MQTT_TOPIC'] = message.topic
        subprocess.run(params['script'], shell=True, env=env)
    else:
        logging.info("No script to execute, use --script")

# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("--script", dest="script", metavar="SCRIPT-NAME", help="Shell script to execute")
parser.add_argument("--mqtt-endpoint", dest="mqtt_endpoint", metavar="HOST[:PORT]", help="AWS IoT endpoint, either 'hostname' or 'hostname:port'")
parser.add_argument("--mqtt-topic", dest="mqtt_topic", metavar="TOPIC", help="Targeted topic")
parser.add_argument("--client-id", dest="client_id", default="MQTT_Listener", help="Client id")
parser.add_argument("--ssl-root-ca", dest="ssl_root_ca", metavar="PEM-FILE", help="Root CA file path")
parser.add_argument("--ssl-cert", dest="ssl_cert", metavar="PEM-FILE", help="Certificate file path")
parser.add_argument("--ssl-key", dest="ssl_key", metavar="PEM-FILE", help="Private key file path")
parser.add_argument("--config", dest="config", metavar="CONFIG-FILE", default="config.ini", help="Config file, default: config.ini")
parser.add_argument("--debug", dest="debug", action="store_true", default=None, help="Enable debugging output")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.config)

params = dict(config['default'].items())
params.update({k:v for k,v in vars(args).items() if v is not None})

endpoint, port = (params.get('mqtt_endpoint') + ":").split(":")[:2]
port = port and int(port) or 8883

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
if params.get('debug'):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = AWSIoTMQTTClient(params.get("client_id"))
myAWSIoTMQTTClient.configureEndpoint(endpoint, port)
myAWSIoTMQTTClient.configureCredentials(params.get("ssl_root_ca"), params.get("ssl_key"), params.get("ssl_cert"))

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe(params.get("mqtt_topic"), 1, custom_callback)

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt as e:
        quit(0)
    except Exception as e:
        print(f"Ignoring: {e}")