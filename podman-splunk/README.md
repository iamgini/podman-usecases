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
- Review and submit; ensure you collected the Token.

Automated way: execute the script after the Splunk setup is completed (check logs)

```shell
# Check logs
$ podman logs -f podman-splunk_splunk_1

# Once finished, copy execute script
$ podman cp ./setup_splunk.sh podman-splunk_splunk_1:/opt/splunk/setup_splunk.sh

$ podman exec -it podman-splunk_splunk_1 /bin/bash /opt/splunk/setup_splunk.sh
```

## Testing Splunk

```shell
export SPLUNK_TOKEN=<your-token>
export SPLUNK_URL=https://192.168.57.1:8088

curl -kv "$SPLUNK_URL/services/collector/event" \
    -H "Authorization: Splunk $SPLUNK_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"event": "I am using IP!", "sourcetype": "manual"}'
```


```shell
curl -kv "https://192.168.57.1:8088/services/collector/event" \
    -H "Authorization: Splunk your-splunk-token" \
    -H "Content-Type: application/json" \
    -d '{"event": "I am using IP!", "sourcetype": "manual"}'
```

## Sample search query

```
source="http:automation" (index="history" OR index="main" OR index="summary")
```

## Delete logs for testing

```
source="http:automation" (index="history" OR index="main" OR index="summary") | delete
```

### Grant can_delete via Splunk Web UI

- Login to Splunk Web as an admin user(usually at https://<your-splunk-host>:8000)
- Go to: Settings → Access Controls → Roles
- Click on the role you want to modify (e.g. admin, or your custom role)
- Scroll down to Capabilities
- ✅ Check the box for can_delete
- Click Save
- 🔄 Log out and log back in to apply changes (sometimes needed)

## Sample JSON output

```json
{"event": "compliance audit", "node_name": "server1", "cis_rule": "1.3.2", "cis_rule_name": "Ensure httpd is disabled"}
```

```shell
curl -kv "$SPLUNK_URL/services/collector/event" -H "Authorization: Splunk $SPLUNK_TOKEN" -H "Content-Type: application/json" -d '{"event": "compliance audit", "node_name": "server1", "cis_rule": "1.3.2", "cis_rule_name": "Ensure httpd is disabled"}'

{
  "event": "compliance audit",
  "node_name": "server1",
  "cis_rule": "1.3.2",
  "cis_rule_name": "Ensure httpd is disabled"
}
{"event": "compliance audit", "node_name": "server1", "cis_rule": "1.3.2", "cis_rule_name": "Ensure httpd is disabled"}
```