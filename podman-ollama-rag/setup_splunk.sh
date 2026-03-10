#!/bin/bash

# Wait for Splunk to start
until sudo /opt/splunk/bin/splunk status | grep "running"; do
  echo "Waiting for Splunk to start..."
  sleep 10
done

# Enable HTTP Event Collector (HEC) if not already enabled
sudo /opt/splunk/bin/splunk http-event-collector enable -auth admin:splunkadmin

# Create a new HTTP Event Collector token (e.g., for automation)
sudo /opt/splunk/bin/splunk http-event-collector create automation \
  -uri https://localhost:8089 \
  -index default \
  -auth admin:splunkadmin

# Retrieve the token
TOKEN=$(sudo /opt/splunk/bin/splunk http-event-collector list automation \
  -uri https://localhost:8089 \
  -auth admin:splunkadmin | grep "token")

echo "HTTP Event Collector token: $TOKEN"

# Output token to a file for later retrieval
echo "$TOKEN" | sudo tee /opt/splunk/token.txt

# Keep the container running
tail -f /dev/null
