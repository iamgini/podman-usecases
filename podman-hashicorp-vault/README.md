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


## References

- [Automating secrets management with HashiCorp Vault and Red Hat Ansible Automation Platform](https://www.redhat.com/en/blog/automating-secrets-management-hashicorp-vault-and-red-hat-ansible-automation-platform)
- [Community.Hashi_Vault](https://docs.ansible.com/ansible/latest/collections/community/hashi_vault/index.html)