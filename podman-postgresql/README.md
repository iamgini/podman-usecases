# PostgreSQL in Podman

```shell
$ cd podman-postgresql
$ podman-compose up -d
# wait for a minute or so as the splunk will take some time to setup.

# Destroy container
$ podman-compose down
```

Test PostgreSQL

```shell
# Connect to postgres
$  psql -h localhost -p 5433 -U admin -d appdb -W
Password:
psql (16.8, server 17.4 (Debian 17.4-1.pgdg120+2))
WARNING: psql major version 16, server major version 17.
         Some psql features might not work.
Type "help" for help.

appdb=#

# See all databases
appdb=# SELECT datname FROM pg_database;
  datname
-----------
 postgres
 appdb
 template1
 template0
(4 rows)

```