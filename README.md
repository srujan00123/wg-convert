# wg-convert

A tiny tool that takes a WireGuard config (standard INI or JSON) and writes a canonical `<name>.conf` ready to drop into `/etc/wireguard/`.

Comes in three flavors:

- **CLI** — pipe in, get a file out
- **Streamlit UI** — paste/upload, download the `.conf`
- **Docker** — one-command deploy, works great behind a reverse proxy (e.g. Coolify + Traefik)

## Input formats

### INI (standard WireGuard)

```ini
[Interface]
PrivateKey = <base64-private-key>
Address = 10.10.60.13/32

[Peer]
PublicKey = <base64-public-key>
Endpoint = vpn.example.com:51820
AllowedIPs = 10.10.11.0/24
```

### JSON

```json
{
  "interface": {
    "PrivateKey": "<base64-private-key>",
    "Address": "10.10.60.13/32"
  },
  "peers": [
    {
      "PublicKey": "<base64-public-key>",
      "Endpoint": "vpn.example.com:51820",
      "AllowedIPs": "10.10.11.0/24"
    }
  ]
}
```

Both produce the same canonical `.conf` output with keys in standard order.

## Install & run locally

Requires [uv](https://docs.astral.sh/uv/) and Python 3.14+.

```bash
git clone https://github.com/<your-fork>/wg-convert.git
cd wg-convert
uv sync
```

### CLI

```bash
# from a file → writes ./myvpn.conf
uv run wg-convert myvpn -i input.txt

# from stdin
cat input.txt | uv run wg-convert myvpn

# print to stdout instead of writing a file
uv run wg-convert myvpn -i input.txt --stdout

# write into a specific directory
uv run wg-convert myvpn -i input.txt -o /etc/wireguard
```

### Streamlit UI

```bash
uv run streamlit run src/wg_convert/app.py
```

Then open http://localhost:8501. Paste your config (or upload a file), enter a name, click **Download `<name>.conf`**.

Shortcut that also works once dependencies are installed:

```bash
uv run python -m wg_convert
```

## Docker

### One-off run

```bash
docker build -t wg-convert .
docker run --rm -p 8501:8501 wg-convert
```

Open http://localhost:8501.

### docker compose

```bash
docker compose up -d --build
```

The compose file exposes port `8501` and includes Traefik labels so it drops straight into a reverse-proxy setup.

Set your domain via an env var (or a `.env` file next to `docker-compose.yml`):

```bash
DOMAIN=wg.example.com docker compose up -d --build
```

## Deploy on Coolify

1. Push this repo (or a fork) to GitHub.
2. In Coolify: **New Resource → Docker Compose** → connect the repo.
3. Set the service domain to whatever you want (e.g. `wg.example.com`). Coolify auto-populates the `SERVICE_FQDN_WGCONVERT_8501` magic variable and wires up Traefik + Let's Encrypt.
4. Deploy.

The included Traefik labels are a fallback for plain Docker setups; Coolify's own routing config takes precedence when deployed there.

## Project layout

```
.
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
└── src/wg_convert/
    ├── __init__.py
    ├── __main__.py   # `python -m wg_convert` → Streamlit
    ├── app.py        # Streamlit UI
    └── cli.py        # CLI + parser/formatter
```

## License

MIT
