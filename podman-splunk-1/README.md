# Splunk in Podman

```shell
$ cd podman-splunk
$ podman-compose up -d
# wait for a minute or so as the splunk will take some time to setup.

# Destroy container
$ podman-compose down
```

- Check the URL: `http://localhost:8000/en-US/account/login?return_to=%2Fen-US%2F`
- Use `admin` as username and the password configured in the `docker-compose.yaml` (eg: `SPLUNK_PASSWORD: splunkadmin`)


## Example use case: Integration with Ansible Controller

- Goto `Settings` -> `Data Inputs`
- Select `Add New` button from `HTTP Event Collector`
- Give name (eg: `automation`) and leave other items as default.
- Review and submit; ensure you collected the **Token**.


## Testing Splunk


```shell
curl -kv "https://192.168.57.1:8088/services/collector/event" \
    -H "Authorization: Splunk your-splunk-token" \
    -H "Content-Type: application/json" \
    -d '{"event": "I am using IP!", "sourcetype": "manual"}'
```


```shell
curl -kv "https://192.168.57.1:8088/services/collector/event" \
    -H "Authorization: Splunk your-splunk-token" \
    -H "Content-Type: application/json" \
    -d '{"event": "I am using IP!", "sourcetype": "manual"}'
```

{"event": "compliance audit", "node_name": "server1", "cis_rule": "1.3.2", "cis_rule_name": "Ensure httpd is disabled"}

curl -kv "$SPLUNK_URL/services/collector/event" -H "Authorization: Splunk $SPLUNK_TOKEN" -H "Content-Type: application/json" -d '{"event": "compliance audit", "node_name": "server1", "cis_rule": "1.3.2", "cis_rule_name": "Ensure httpd is disabled"}'

{
  "event": "compliance audit",
  "node_name": "server1",
  "cis_rule": "1.3.2",
  "cis_rule_name": "Ensure httpd is disabled"
}
{"event": "compliance audit", "node_name": "server1", "cis_rule": "1.3.2", "cis_rule_name": "Ensure httpd is disabled"}