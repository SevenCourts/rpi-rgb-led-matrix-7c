# How to start panel emulator

Choose the version to start and run following command replacing `__VERSION__` with choosen version.
`docker pull ghcr.io/sevencourts/rpi-rgb-led-matrix-7c:__VERSION__`.

Then run container with command

```sh
docker container run \
    -it \
    --rm \
    -e TABLEAU_SERVER_BASE_URL='https://staging.server.sevencourts.com' \
    -p 8888:8888 \
    ghcr.io/sevencourts/rpi-rgb-led-matrix-7c:__VERSION__
```
