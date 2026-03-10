# Ollama in Podman

```shell
$ cd podman-splunk
$ podman-compose up -d
# wait for a minute or so as the splunk will take some time to setup.
```

Pull your models (exec into the ollama container to keep it isolated):

```shell
podman exec -it ollama ollama pull llama3.2
podman exec -it ollama ollama pull nomic-embed-text
```

```shell
# Destroy container
$ podman-compose down
```

## How to access the UI

- Open `http://localhost:3001`
- Select `ollama` in the LLM Preference page.
  - Ollama Base URL: `http://ollama:11434`
  - Model: `Ollama`
  - Embedding Model: Choose `nomic-embed-text:latest`
