#!/bin/bash

# The mqtt-listener will pass two environment variables:
#
# MQTT_TOPIC   - the topic name where the message was received from,
#                e.g. iotbutton/G123ABCD1234ABCD
#
# MQTT_PAYLOAD - Message received from the topic, usually JSON
#                formatted in which case 'jq' can be used to parse it.
#                e.g. '{ "serialNumber": "G123ABCD1234ABCD", "clickType": "SINGLE" }'

echo "MQTT_TOPIC: ${MQTT_TOPIC}"
echo "MQTT_PAYLOAD: ${MQTT_PAYLOAD}"

# Use 'jq' to parse JSON payload
# e.g. to extract "clickType" from AWS IoT Button message
CLICK_TYPE=$(jq -r .clickType <<< ${MQTT_PAYLOAD})

notify-send --urgency=normal --icon info "${CLICK_TYPE} click message from ${MQTT_TOPIC}" "${MQTT_PAYLOAD}"
