```shell
$ podman build -t nfs:alpine .

$ podman run -d --name nfs-server --privileged -v ~/nfs-dir:/data nfs:alpine
```