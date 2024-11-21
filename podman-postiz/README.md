# Postiz in Podman

```shell
$ cd podman-postiz
$ podman-compose up -d
# wait for a minute or so as the splunk will take some time to setup.

# Destroy container
$ podman-compose down
```

- Check the URL: `http://localhost:8000/en-US/account/login?return_to=%2Fen-US%2F`
- Use `admin` as username and the password configured in the `docker-compose.yaml` (eg: `SPLUNK_PASSWORD: splunkadmin`)
