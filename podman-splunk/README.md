# Splunk in Podman

```shell
cd podman-splunk
podman-compose up -d
# wait for a minute or so as the splunk will take some time to setup.
podman-compose down
podman images
```

- Check the URL: `http://localhost:8000/en-US/account/login?return_to=%2Fen-US%2F`
- Use `admin` as username and the password configured in the `docker-compose.yaml` (eg: `SPLUNK_PASSWORD: splunkadmin`)


## Example use case: Integration with Ansible Controller

- Goto `Settings` -> `Data Inputs`
- Select `Add New` button from `HTTP Event Collector`
- Give name (eg: `aapcollector`) and leave other items as default.
- Review and submit; ensure you collected the Token.


## Testing Splunk


```shell
curl "http://localhost:8000/services/aapcollector" \
    -H "Authorization: Splunk a3c4cc74-61ba-47b4-a1b4-ab08576b1d77" \
    -d '{"event": "Hello, world!", "sourcetype": "manual"}'
```