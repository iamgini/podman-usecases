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

After installing the recommended plugins, Jenkins will ask you to create the `Administrator` user. Follow the instruction to create administrator account

## stop the jenkins server

Once finished, you can delete/stop the Jenkins server

```shell
$ podman-compose down
```


## Appendix

### Start Jenkins inside a container

Refer **[Docker Hub](https://hub.docker.com/r/jenkins/jenkins/)**
## Run `jenkins` as a docker container

```shell
$ docker run \
  --name jenkins \
  --detach \
  --volume jenkins-data:/var/jenkins_home \
  --publish 8080:8080 \
  --publish 50000:5000 \
  jenkins/jenkins:lts
```  

where,
- `--name` - name of the container
- `--detach` or `-d` - detached mode (in background)
- `--volume jenkins-data:/var/jenkins_home` - bind named volume (will create a directory in `/var/lib/docker/volumes/`)
- `--publish 8080:8080`  or `-p` - map or export host port `8080` to container port `8080`
- `jenkins/jenkins:lts` - docker image to be used.
## Get the Password

- First Admin password can be found at `/var/jenkins_home/secrets/initialAdminPassword`

```
$ sudo docker exec -it 198b7deb5f7d /bin/bash
jenkins@198b7deb5f7d:/$ cat /var/jenkins_home/secrets/initialAdminPassword
8d53672878b24941a1cdf3df3c8ec8cc
jenkins@198b7deb5f7d:/$ exit
exit
```

- or check `docker logs CONTAINER_ID` and get the password.   

## Login to Jenkins GUI for the first time 

- Open a web browser and goto `localhost:8080`
- enter the password collected from previous step.
- Install Suggested plugins
- Create the first time user
- confirm jenkins url

## Sample docker-compose.yml

```
version: '3'
services:
  jenkins:
    tty: true
    stdin_open: true
    container_name: jenkins
    image: jenkins/jenkins
    ports:
      - "8080:8080"
    volumes:
      - "$PWD/jenkins_home:/var/jenkins_home"
    networks:
      - net
networks:
 net:
```
