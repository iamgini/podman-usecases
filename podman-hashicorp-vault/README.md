# Hashicorp Vault in Podman

```shell
$ cd podman-podman-hashicorp-vault
$ podman-compose up -d

# Destroy container
$ podman-compose down
```

## First time login steps:

Open your browser and go to: `http://localhost:8200`

When prompted for the token, use: `root` (This is the VAULT_DEV_ROOT_TOKEN_ID we passed in the environment.)
