# Elastic and Kibana in Podman

```shell
$ cd podman-elastic-kibana
$ podman-compose up -d
# wait for a minute or so as the splunk will take some time to setup.

# Destroy container
$ podman-compose down
```

## Get Kibana URL
Run the command below to get initial Kibana URL and port.

$ podman logs kib01 | grep 5601