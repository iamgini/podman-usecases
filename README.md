# podman-usecases
Application using Podman and Containers

```shell
cd podman-experiments
podman-compose up -d
podman-compose down
podman images
```

## Troubleshooting

### Write permission error while mounting local directory 

Error sample:

```
$ podman run --rm -it -v ${PWD}/data/:/docs squidfunk/mkdocs-material new .
INFO     -  Writing config file: ./mkdocs.yml
Traceback (most recent call last):
  File "/usr/local/bin/mkdocs", line 8, in <module>
    sys.exit(cli())
             ^^^^^
  File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1130, in __call__
    return self.main(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1055, in main
    rv = self.invoke(ctx)
         ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1657, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1404, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/click/core.py", line 760, in invoke
    return __callback(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/mkdocs/__main__.py", line 297, in new_command
    new.new(project_directory)
  File "/usr/local/lib/python3.11/site-packages/mkdocs/commands/new.py", line 43, in new
    with open(config_path, 'w', encoding='utf-8') as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [Errno 13] Permission denied: './mkdocs.yml'
```

Solution: Apply correct SELinux permissions

```shell
$ chcon -Rt svirt_sandbox_file_t data/
```
