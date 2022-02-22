# Jenkins inside  container using podman (machine)

This is a simple `docker-compose.yaml` for quickly spinning up a Jenkins server using podman (or docker).

Since I am using podman on mac (with `podman machine`), I did not test it with docker. You need to enable `/var/run/docker.sock:/var/run/docker.sock` volume if you are using Docker.

## How to use this repo

```shell
## clone this repo
$ git clone https://github.com/ginigangadharan/podman-usecases.git

## switch to podman-jenkins directory
$ cd podman-jenkins

## Start jenkins.
## install podman-compose if not yet
$ podman-compose up -d

## login to podman container to collect password
$ podman exec -it de1c01738ff7 /bin/bash 
root@de1c01738ff7:/# cat /var/jenkins_home/secrets/initialAdminPassword
ccccd8f2b5e9403f87188bce93c33eef
root@de1c01738ff7:/# exit
exit

## stop the jenkins server
$ podman-compose down
```