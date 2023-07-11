# Quick wordpress site using Podman compose

```shell
$ podman-compose -f compose.yaml up -d

$  podman ps
CONTAINER ID  IMAGE                               COMMAND               CREATED        STATUS        PORTS                 NAMES
888b222ec704  docker.io/library/mariadb:latest    --default-authent...  3 minutes ago  Up 3 minutes                        podman-wordpress_db_1
36029e026792  docker.io/library/wordpress:latest  apache2-foregroun...  2 minutes ago  Up 3 minutes  0.0.0.0:8081->80/tcp  podman-wordpress_wordpress_1
```


**Warning: NOT TESTED**

```shell
podman pod create --name wordpress --publish 8081:80


podman run --detach --pod wordpress \
   -e MYSQL_ROOT_PASSWORD="password" \
   -e MYSQL_DATABASE=wordpressdb \
   -e MYSQL_USER=wpuser \
   -e MYSQL_PASSWORD="password" \
   --name wordpressdb -d docker.io/library/mariadb


podman run --detach --pod wordpress \
   -e WORDPRESS_DB_HOST=localhost \
   -e WORDPRESS_DB_NAME=wordpressdb \
   -e WORDPRESS_DB_USER=wpuser \
   -e WORDPRESS_DB_PASWORD="password" \
   --name mywp docker.io/wordpress
```   