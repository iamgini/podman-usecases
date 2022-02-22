# Jenkins inside  container using podman (machine)

This is a simple `docker-compose.yaml` for quickly spinning up a Jenkins server using podman (or docker).

Since I am using podman on mac (with `podman machine`), I did not test it with docker. You need to enable `/var/run/docker.sock:/var/run/docker.sock` volume if you are using Docker.

## Using podman on macOS with podman machine

You can use `podman` on macOS by installing the `podman machine` which is a virtualmachine. Refer [poman cheatsheet](https://www.iamgini.com/podman) for more details.

```shell
## start podman machine if not yet
$ podman machine start
```

## How to use this repo

```shell
## clone this repo
$ git clone https://github.com/ginigangadharan/podman-usecases.git

## switch to podman-jenkins directory
$ cd podman-jenkins

## Start jenkins.
## install podman-compose if not yet
$ mkdir jenkins_configuration
```

## Start Jenkins server inside container

```shell
$ podman-compose up -d
```

## login to podman container to collect initial password

```shell
$ podman exec -it CONTAINER_ID /bin/bash 
root@CONTAINER_ID:/# cat /var/jenkins_home/secrets/initialAdminPassword
ccccd8f2b5e9403f87188bce93c33eef
root@CONTAINER_ID:/# exit
exit
```
## Access the Jenkins server

Now you can access the Jenkins server in a browser using `http://localhost:8080/`. Login with the initial password and install recommended plugins as needed.

## Creating the first administrator user

After installing the recommended plugins, Jenkins will ask you to create the Administrato user. Follow the instruction to create administrator account

## stop the jenkins server

Once finished, you can delete/stop the Jenkins server

```shell
$ podman-compose down
```