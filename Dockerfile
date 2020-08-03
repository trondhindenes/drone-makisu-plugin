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
WORKDIR /makisu-internal
COPY --from=0 /workspace/github.com/uber/makisu/bin/makisu/makisu.linux /makisu-internal/makisu
COPY --from=0 /temp/repo/makisu/assets/cacerts.pem /makisu-internal/certs/cacerts.pem
RUN chmod +x /makisu-internal/makisu
ADD script.sh /bin/
RUN chmod +x /bin/script.sh
ENTRYPOINT /bin/script.sh