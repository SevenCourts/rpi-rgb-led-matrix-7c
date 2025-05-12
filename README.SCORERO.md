# How to install and start SevenCourts M1 scoreboard emulator

1. Install Docker, on Windows start Docker Desktop

2. In shell login to GitHub Docker Image Registry with the GitHub Personal Access Token `[PAT]`.
The `[PAT]` is created with <https://github.com/settings/tokens>.

```shell
echo '[PAT]' | docker login ghcr.io -u shinych --password-stdin
```

3. Choose the version of scoreboard firmware emulator to start.
In the steps below, it is `eb3d738`.

4. Pull the SevenCourts M1 emulator image:

```shell
docker pull ghcr.io/sevencourts/rpi-rgb-led-matrix-7c:eb3d738 
```

5. Start this image:

```shell
docker container run -it --rm -e TABLEAU_SERVER_BASE_URL='https://staging.server.sevencourts.com' -p 8888:8888 ghcr.io/sevencourts/rpi-rgb-led-matrix-7c:eb3d738 
```

On Windows, you might need to start it via WINPTY:

```shell
winpty docker container run -it --rm -e TABLEAU_SERVER_BASE_URL='https://staging.server.sevencourts.com' -p 8888:8888 ghcr.io/sevencourts/rpi-rgb-led-matrix-7c:eb3d738
```

6. After it is started, the scoreboard emulator can be opened <http://localhost:8888> in browser.

7. The Admin UI is available via <https://staging.server.sevencourts.com/panel-admin/[PANEL-ID]>

Where `[PANEL-ID]` is taken from the emulator log window.

7. The same `[PANEL-ID]` has also to be used in the REST requests.
