podman build -t jekyll:1.1 .

podman run --rm -v ${PWD}:/data:Z -it localhost/jekyll:1.1 /bin/sh


```shell
## Launch the container 
podman run --rm -p 4000:4000 -v ${PWD}:/data:Z -it localhost/jekyll:1.3 sh -c "bundle install && bundle exec jekyll serve --host 0.0.0.0 --incremental"



## speed up page build
jekyll serve --incremental
###### or ######
jekyll serve --watch --limit_posts 1

#### to 0.0.0.0 host
bundle exec jekyll serve --host 0.0.0.0 --incremental
```

### Install `curl` inside Alpine container

```shell
# apk add curl
```