#!/bin/sh
# Dispatch: serve (default) or preflight

CMD="${1}"

case "${CMD}" in
  preflight)
    shift
    exec python3 /usr/local/bin/preflight.py "$@"
    ;;
  serve)
    shift
    exec reveal-md "$@"
    ;;
  *)
    # Default: pass everything straight to reveal-md (backwards compatible)
    exec reveal-md "$@"
    ;;
esac
