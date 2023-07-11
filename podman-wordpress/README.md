

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