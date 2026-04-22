FROM node:22-alpine

# Install Hugo extended (needed for Tailwind/SCSS)
RUN apk add --no-cache go git hugo

WORKDIR /site

# Cache npm deps as a layer
COPY package.json package-lock.json* ./
RUN npm install

ENTRYPOINT ["hugo"]


podman run --rm \
  -p 1313:1313 \
  -v ${PWD}:/site:Z \
  -it your-hugo-dev-image \
  server --bind 0.0.0.0 --disableFastRender