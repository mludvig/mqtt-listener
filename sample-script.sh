#!/bin/bash

echo "MQTT_TOPIC: ${MQTT_TOPIC}"
echo "MQTT_PAYLOAD: ${MQTT_PAYLOAD}"

SERIAL_NUMBER=$(jq -r .serialNumber <<< ${MQTT_PAYLOAD})

notify-send --urgency=normal --expire-time 10000 --icon error "MQTT Message from ${MQTT_TOPIC}" "${MQTT_PAYLOAD}\n${SERIAL_NUMBER}"
