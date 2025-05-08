# Gitlab CE in Podman

## Prepare environment

Create volumes

```shell
podman volume create gitlab_config
podman volume create gitlab_logs
podman volume create gitlab_data
```

Create secret

```shell
echo "SuperSecret123" | podman secret create gitlab_root_password -
```

## Start containers

```shell
$ cd podman-gitlab-ce
$ podman-compose up -d
```

## Stop and Destroy containers

```shell
# Destroy container
$ podman-compose down
```


## Running without compose

```shell
$ podman run -d \
  --name gitlab-ce \
  -p 8443:443 \
  -p 8080:80 \
  -p 2222:22 \
  -v gitlab_config:/etc/gitlab:Z \
  -v gitlab_logs:/var/log/gitlab:Z \
  -v gitlab_data:/var/opt/gitlab:Z \
  -e GITLAB_OMNIBUS_CONFIG="external_url 'http://gitlab.lab.iamgini.com:8080'; gitlab_rails['initial_root_password'] = 'SuperSecret123'" \
  --hostname gitlab.lab.iamgini.com \
  gitlab/gitlab-ce:16.11.1-ce.0

podman run -d \
  --name gitlab-ce \
  -p 8443:443 \
  -p 8181:80 \
  -p 2222:22 \
  -v gitlab_config:/etc/gitlab:Z \
  -v gitlab_logs:/var/log/gitlab:Z \
  -v gitlab_data:/var/opt/gitlab:Z \
  -e GITLAB_OMNIBUS_CONFIG="external_url 'http://localhost:8181'; gitlab_rails['initial_root_password'] = 'SuperSecret123'" \
  --hostname gitlab.lab.iamgini.com \
  gitlab/gitlab-ce:16.11.1-ce.0
```

## Troubleshooting

Check logs

```shell
$ podman logs -f gitlab-ce
```