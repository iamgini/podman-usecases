curl -kv "http://localhost:8000/services/collector" \
    -H "Authorization: Splunk 22f6daa9-ce22-4139-b643-136cc0d8bed6" \
    -d '{"event": "Hello, world!", "sourcetype": "manual"}'
