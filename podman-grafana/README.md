# Grafana in Podman

```shell
$ cd podman-grafana
$ podman-compose up -d

# Destroy container
$ podman-compose down
```

## Adding AAP Dashboard.


## Troubleshooting

Fix the SELinux and permission of `prometheus.yml`

```shell
$ chmod 644 ./prometheus.yml
$ chcon -R -t container_file_t ./prometheus.yml
```

## References

- [Monitoring Ansible Automation Platform using User-Defined Projects and Grafana](https://www.redhat.com/en/blog/monitoring-ansible-automation-platform-using-user-defined-projects-and-grafana)
- [github.com/leoaaraujo/aap-dashboard](https://github.com/leoaaraujo/aap-dashboard)