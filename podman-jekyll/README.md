podman build -t jekyll:1.1 .

podman run --rm -v ${PWD}:/data:Z -it localhost/jekyll:1.1 /bin/sh


```shell
## speed up page build
jekyll serve --incremental
###### or ######
jekyll serve --watch --limit_posts 1
```


Type	Name	Content	TTL
A
@
185.199.109.153
Auto
A
@
185.199.111.153
Auto
A
@
185.199.110.153
Auto
A
@
185.199.108.153
Auto
