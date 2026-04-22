# Podman for AI Model

```shell
# Usage:
#   podman-compose up -d        # start
#   podman-compose down         # stop
#   podman-compose logs -f      # follow logs
```

```shell
# First run - pull the model:
podman exec -it ollama-local ollama pull gemma4:e4b
```