# 語彙練習帳 — N2 vocabulary practice
#
# Build:  docker build -t goi .
# Run:    docker run -p 8788:8788 -v goi-data:/app/data goi
# Open:   http://localhost:8788
#
# Alpine keeps this small, and the app needs nothing from PyPI — only openssl,
# for the self-signed certificate that phones need in order to use the mic.

FROM python:3.12-alpine

RUN apk add --no-cache openssl

# Run as a normal user. The app writes only to /app/data, which is a volume.
RUN adduser -D -u 10001 goi
WORKDIR /app

COPY index.html server.py ./
RUN mkdir -p /app/data && chown -R goi:goi /app

USER goi
VOLUME ["/app/data"]
EXPOSE 8788

# A container must bind every interface; the port mapping decides who can
# actually reach it. TLS is off by default because the usual way in is
# http://localhost:8788 through that mapping, and browsers already treat
# localhost as a secure origin — so the microphone works with no certificate
# and no warning. Turn it on with GOI_TLS=1 when a phone needs to connect,
# and set GOI_SAN to the host's LAN address so the certificate matches.
ENV GOI_HOST=0.0.0.0 \
    GOI_PORT=8788 \
    GOI_TLS=0 \
    PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import os,sys,urllib.request,ssl; \
p=os.environ.get('GOI_PORT','8788'); \
s=(os.environ.get('GOI_TLS','0').lower() not in ('0','false','no','off')); \
u=('https' if s else 'http')+'://127.0.0.1:'+p+'/api/health'; \
c=ssl._create_unverified_context() if s else None; \
sys.exit(0 if urllib.request.urlopen(u,timeout=2,context=c).status==200 else 1)"

ENTRYPOINT ["python", "server.py"]
