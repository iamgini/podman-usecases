# Gitea in Podman

Creating an administrator account is optional. The first registered user will automatically become an administrator.

## Start containers

```shell
$ cd podman-gitea
$ podman-compose up -d
```

## Stop and Destroy containers

```shell
# Destroy container
$ podman-compose down
```

## Troubleshooting

Remove volumes for a fresh setup

```shell
$ podman volume rm podman-gitea_gitea-data podman-gitea_gitea-mysql-data
```

Check logs

```shell
$ podman logs -f gitea
```