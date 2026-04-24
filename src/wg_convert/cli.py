import argparse
import json
import re
import sys
from pathlib import Path


WG_KEYS = {
    "interface": ["PrivateKey", "Address", "ListenPort", "DNS", "MTU", "Table", "PreUp", "PostUp", "PreDown", "PostDown"],
    "peer": ["PublicKey", "PresharedKey", "Endpoint", "AllowedIPs", "PersistentKeepalive"],
}


def parse_ini(text: str) -> dict:
    sections: dict[str, list[dict]] = {"Interface": [], "Peer": []}
    current: dict | None = None
    current_name: str | None = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        m = re.match(r"\[(\w+)\]", line)
        if m:
            current_name = m.group(1)
            current = {}
            sections.setdefault(current_name, []).append(current)
            continue
        if current is None or "=" not in line:
            continue
        k, v = line.split("=", 1)
        current[k.strip()] = v.strip()
    return sections


def parse_json(text: str) -> dict:
    data = json.loads(text)
    iface = data.get("interface") or data.get("Interface") or {}
    peers = data.get("peers") or data.get("Peers") or []
    if isinstance(peers, dict):
        peers = [peers]
    return {"Interface": [iface] if iface else [], "Peer": peers}


def format_conf(sections: dict) -> str:
    out: list[str] = []
    for iface in sections.get("Interface", []):
        out.append("[Interface]")
        for key in WG_KEYS["interface"]:
            if key in iface:
                out.append(f"{key} = {iface[key]}")
        for k, v in iface.items():
            if k not in WG_KEYS["interface"]:
                out.append(f"{k} = {v}")
        out.append("")
    for peer in sections.get("Peer", []):
        out.append("[Peer]")
        for key in WG_KEYS["peer"]:
            if key in peer:
                out.append(f"{key} = {peer[key]}")
        for k, v in peer.items():
            if k not in WG_KEYS["peer"]:
                out.append(f"{k} = {v}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def load(text: str) -> dict:
    stripped = text.lstrip()
    if stripped.startswith("{"):
        return parse_json(text)
    return parse_ini(text)


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert a WireGuard config to <name>.conf")
    ap.add_argument("name", help="Output filename (without .conf)")
    ap.add_argument("-i", "--input", help="Input file (default: stdin)")
    ap.add_argument("-o", "--out-dir", default=".", help="Output directory (default: cwd)")
    ap.add_argument("--stdout", action="store_true", help="Write to stdout instead of a file")
    args = ap.parse_args()

    text = Path(args.input).read_text() if args.input else sys.stdin.read()
    if not text.strip():
        print("error: empty input", file=sys.stderr)
        return 2

    sections = load(text)
    if not sections.get("Interface"):
        print("error: no [Interface] section found", file=sys.stderr)
        return 2

    conf = format_conf(sections)

    if args.stdout:
        sys.stdout.write(conf)
        return 0

    out_path = Path(args.out_dir) / f"{args.name}.conf"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(conf)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
