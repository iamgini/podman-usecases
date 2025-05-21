#!/bin/bash
export SPLUNK_TOKEN=c23e9c42-00b3-4326-ac4f-b5e5bc06c100
export SPLUNK_URL=https://192.168.57.1:8088

curl -kv "$SPLUNK_URL/services/collector/event" \
    -H "Authorization: Splunk $SPLUNK_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"event": "I am using IP!", "sourcetype": "manual"}'