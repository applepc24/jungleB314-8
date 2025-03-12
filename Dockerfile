FROM docker.io/python:3.13 AS builder

RUN mkdir -p /opt/web/
WORKDIR /opt/web

ADD requirements.txt ./
RUN python -m venv .venv
RUN .venv/bin/python -m pip install -r requirements.txt

FROM docker.io/python:3.13

RUN mkdir -p /opt/web/
WORKDIR /opt/web

COPY --from=builder /opt/web/.venv /opt/web/.venv
ADD . /opt/web/

ENTRYPOINT ["/opt/web/.venv/bin/python", "app.py"]
