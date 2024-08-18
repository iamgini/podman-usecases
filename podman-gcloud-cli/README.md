# gcloud CLI in Podman

```shell
$ cd podman-gcloud-cli
$ podman-compose up -d

# Go inside container and use gcloud CLI
$ podman exec -it gcloud-cli /bin/bash
root@5a95219e4ff4:/# gcloud --version
Google Cloud SDK 488.0.0
alpha 2024.08.09
beta 2024.08.09
bq 2.1.8
bundled-python3-unix 3.11.9
core 2024.08.09
gcloud-crc32c 1.0.0
gsutil 5.30

# Destroy container
$ podman-compose down
```
