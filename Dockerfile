FROM golang:1.12
WORKDIR /temp/repo
RUN \
    git clone https://github.com/uber/makisu.git
WORKDIR /workspace/github.com/uber/makisu
RUN \
    cp /temp/repo/makisu/Makefile . &&\
    cp /temp/repo/makisu/go.mod . &&\
    cp /temp/repo/makisu/go.sum . &&\
    make vendor
RUN \
    cp /temp/repo/makisu/.git -r . &&\
    cp /temp/repo/makisu/bin -r . &&\
    cp /temp/repo/makisu/lib -r . &&\
    make lbins

FROM ubuntu:20.04
WORKDIR /temp
RUN apt-get update && apt-get install -y wget
RUN wget https://amazon-ecr-credential-helper-releases.s3.us-east-2.amazonaws.com/0.4.0/linux-amd64/docker-credential-ecr-login

FROM python:3.8
WORKDIR /makisu-internal
COPY --from=0 /workspace/github.com/uber/makisu/bin/makisu/makisu.linux /makisu-internal/makisu
COPY --from=0 /temp/repo/makisu/assets/cacerts.pem /makisu-internal/certs/cacerts.pem
COPY --from=1 /temp/docker-credential-ecr-login /bin/docker-credential-ecr-login
COPY script.py /bin/script.py
RUN \
    chmod +x /makisu-internal/makisu &&\
    chmod +x /bin/docker-credential-ecr-login &&\
    chmod +x /bin/script.py
ENV PYTHONUNBUFFERED=1
ENV SSL_CERT_DIR /makisu-internal/certs
ENTRYPOINT /bin/script.py