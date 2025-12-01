FROM python:3.9-slim-bullseye

RUN apt-get update && \
    env DEBIAN_FRONTEND=noninteractive \
        apt-get install -yq --no-install-recommends --no-install-suggests jq && \
    rm -rf /var/lib/apt/lists/*

RUN pip install \
        Pillow \
        requests \
        python-dateutil \
        RGBMatrixEmulator==0.13.3

WORKDIR "/app"
ENTRYPOINT ["/app/m1_emulator.sh"]

RUN mkdir -p /opt/7c && touch /opt/7c/panel_dev.conf
ENV PANEL_CONFIG=/opt/7c/panel_dev.conf

ENV TABLEAU_SERVER_BASE_URL='https://dev.server.sevencourts.com'

COPY ./fonts ./fonts
COPY ./images ./images
COPY \
    ./commit-id \
    ./commit-date \
    ./emulator_config.json \
    ./m1_emulator.sh \
    ./m1.py \
    ./m1.sh \
    ./samplebase.py \
    ./sevencourts.py \
    ./

RUN jq '.browser.target_fps = 1' ./emulator_config.json
