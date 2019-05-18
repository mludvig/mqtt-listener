#!/usr/bin/env python3

# Execute a script upon AWS IoT MQTT message reception
# Inspired by aws-iot-device-sdk-python/samples/basicPubSub/basicPubSub.py

import os
import logging
import time
import argparse
import json
import subprocess

from config import config

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Custom MQTT message callback
def custom_callback(client, userdata, message):
    logging.debug(f"Received a new message from {message.topic}: ")
    logging.debug(f"Payload: {message.payload}")
    if args.script:
        logging.debug(f"Executing: {args.script}")
        env = os.environ.copy()
        env['MQTT_PAYLOAD'] = message.payload
        env['MQTT_TOPIC'] = message.topic
        subprocess.run(args.script, shell=True, env=env)
    else:
        logging.info("No script to execute, use --script")

# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("--mqtt-endpoint", dest="endpoint", default=config.mqtt_endpoint, help="AWS IoT endpoint, either 'hostname' or 'hostname:port'")
parser.add_argument("--ssl-root-ca", dest="ssl_root_ca", default=config.ssl_root_ca, help="Root CA file path")
parser.add_argument("--ssl-cert", dest="ssl_cert", default=config.ssl_cert, help="Certificate file path")
parser.add_argument("--ssl-key", dest="ssl_key", default=config.ssl_key, help="Private key file path")
parser.add_argument("--client-id", dest="client_id", default="ScreenTime", help="Targeted client id")
parser.add_argument("--topic", dest="topic", default=config.topic, help="Targeted topic")
parser.add_argument("--script", dest="script", required=False, help="Shell script to execute")
parser.add_argument("--debug", dest="debug", action="store_true", help="Enable debugging output")

args = parser.parse_args()
endpoint, port = (args.endpoint + ":").split(":")[:2]
port = port and int(port) or 8883

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
if args.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = AWSIoTMQTTClient(args.client_id)
myAWSIoTMQTTClient.configureEndpoint(endpoint, port)
myAWSIoTMQTTClient.configureCredentials(args.ssl_root_ca, args.ssl_key, args.ssl_cert)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe(args.topic, 1, custom_callback)

while True:
    try:
        time.sleep(2)
    except KeyboardInterrupt as e:
        quit(0)
    except Exception as e:
        print(f"Ignoring: {e}")
