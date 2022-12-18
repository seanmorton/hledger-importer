FROM logiqx/python-lxml:3.10-alpine3.15

# TODO switch back to stable repo once hledger becomes available (hopefully alpine 3.16)
RUN apk update && \
    apk add --update git && \
    apk add --update openssh && \
    apk add hledger --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community

RUN pip install --no-cache-dir getmail6

RUN mkdir -p /home/hledger
RUN addgroup hledger && \
    adduser hledger -G hledger --disabled-password && \
    chown -R hledger /home/hledger

USER hledger
WORKDIR /home/hledger

COPY cmd.sh ./
CMD ["./cmd.sh"]
