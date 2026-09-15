# Running in Docker

The whole app is one HTML file and one Python file, so the image is small and
needs nothing from PyPI. Use this if you'd rather not install Python on the
host, or you want it running on a home server.

---

## Quick start

```
docker compose up -d
```

Then open **<http://localhost:8788>**.

That builds the image, starts the container in the background, and creates a
named volume for your data. To watch the log: `docker compose logs -f`. To
stop: `docker compose down` — your progress survives, it's in the volume.

### Without Compose

```
docker build -t goi .
docker run -d --name goi -p 8788:8788 -v goi-data:/app/data goi
```

---

## Where your data lives

Everything you'd hate to lose — progress, voice recordings, the certificate —
is written to `/app/data` inside the container, which is mounted as the named
volume `goi-data`. The image itself is disposable: rebuild it whenever, your
data is untouched.

**To keep the files somewhere you can see them**, swap the volume for a bind
mount. In `docker-compose.yml`:

```yaml
    volumes:
      - ./data:/app/data
```

or on the command line, `-v "$PWD/data:/app/data"`.

> **If you bind-mount**, the host directory must be writable by UID **10001**
> — the image runs as a non-root user called `goi`. Either
> `mkdir -p data && sudo chown 10001:10001 data` first, or add
> `user: "$(id -u):$(id -g)"` to the service so it runs as you.

**Back it up** by copying that directory, or from the volume:

```
docker run --rm -v goi-data:/data -v "$PWD":/out alpine \
  tar czf /out/goi-backup.tgz -C /data .
```

---

## Studying from your phone

This needs one more step than the host install, for a reason worth
understanding.

Browsers only offer the microphone on a **secure origin**. `localhost` counts,
so the default `http://localhost:8788` already works — the mic is available
with no certificate at all. A plain `http://192.168.…` address does **not**
count; on it, `navigator.mediaDevices` doesn't even exist, so there's no
recording and no 🎤 Speak. For a phone, you need HTTPS.

The catch: inside a container the app can only see the *container's* address
(something like `172.17.0.2`), which no phone can reach. So you have to tell
it your computer's real LAN address, or the certificate won't match and the
phone will refuse the connection outright.

**1. Find your computer's LAN address** (on the host, not in the container):

```
ip route get 1.1.1.1 | awk '{print $7; exit}'     # Linux
ipconfig getifaddr en0                            # macOS
```

**2. Put it in `docker-compose.yml`** and uncomment both lines:

```yaml
    environment:
      GOI_TLS: "1"
      GOI_SAN: "192.168.1.50"     # your address, not this one
```

**3. Restart:** `docker compose up -d --force-recreate`

**4. On the phone**, open `https://192.168.1.50:8788`. It warns the certificate
isn't trusted — tap **Advanced → Proceed**. It's signed by your own machine,
for your own machine; nothing external vouches for it, which is precisely why
the warning appears. Then allow the microphone.

If you change `GOI_SAN` later, delete the old certificate so a new one is made
for the new address:

```
docker compose down
docker run --rm -v goi-data:/data alpine rm -rf /data/cert
docker compose up -d --force-recreate
```

**Anyone on that network can read and change your data.** There is no password
— encryption is not authentication. Home wifi only.

---

## Settings

All optional; the defaults are what the image ships with.

| Variable | Default | What it does |
| --- | --- | --- |
| `GOI_HOST` | `0.0.0.0` | Bind address. A container must bind everything; the port mapping is what limits access. |
| `GOI_PORT` | `8788` | Port inside the container. Change the mapping too. |
| `GOI_TLS` | `0` | `1` serves HTTPS with a self-signed certificate. Needed only for phone access. |
| `GOI_SAN` | — | Address(es) the certificate must cover, comma separated. Set this to your host's LAN IP whenever `GOI_TLS=1`. |

Flags still work if you prefer them — `docker run … goi --port 9000 --https`.

### A different port

```yaml
    ports:
      - "9000:8788"
```

Only the left side changes. `GOI_PORT` stays `8788` because that's the port
inside the container.

---

## When something goes wrong

| What you see | What it means | Fix |
| --- | --- | --- |
| `bind: address already in use` | Something else holds 8788 on the host | Map a different host port: `"9000:8788"` |
| Container restarts forever | Usually a write failure on a bind mount | `docker compose logs`; check the ownership note above |
| `Permission denied` on `/app/data` | Bind-mounted directory not writable by UID 10001 | `sudo chown 10001:10001 data`, or add `user:` to the service |
| Health shows `unhealthy` | The app isn't answering `/api/health` | `docker compose logs`. If you set `GOI_TLS=1`, the check follows it automatically |
| Phone: "connection is not private" | Self-signed certificate | **Advanced → Proceed** |
| Phone refuses to connect at all | Certificate doesn't cover that address | Set `GOI_SAN` to the host's LAN IP, delete `data/cert`, recreate |
| 🎤 Speak greyed out on the phone | You're on a plain `http://` LAN address | Set `GOI_TLS=1` and `GOI_SAN`, then use the `https://` URL |
| ▶ Model greyed out | No Japanese text-to-speech voice | That's the *browser's* voice, from your desktop OS — nothing the container can supply. See the main README |

---

## What's in the image

`python:3.12-alpine`, plus `openssl` for certificate generation. The app
itself is `index.html` and `server.py` — no pip install, no build step, no
network access needed at runtime. It runs as UID 10001, not root, and the only
writable path it needs is `/app/data`.
