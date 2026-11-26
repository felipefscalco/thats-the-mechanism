#!/usr/bin/env python3
"""r8 credit ledger hygiene (pattern learned from MoneyPrinterTurbo material._safe_public_url /
_material_source_record, MIT; re-implemented, not vendored).

A credit row is public: it ends up in photo_credits.md, the publish pack and the repo. Download URLs can carry API
keys, signed tokens or basic-auth, and records can carry local paths. So rows are REBUILT from a whitelist:
  safe_public_url(u)   -> http(s) page URL with query, fragment and userinfo stripped, or None (other schemes, file
                          paths, user:pass@host, missing host)
  credit_record(row)   -> whitelisted fields only; file paths reduced to a repo-relative path or a bare file name;
                          free text scrubbed of local paths and token-looking strings
  persist(rows, ...)   -> writes CREDITS.csv + photo_credits.md atomically; a failure is logged and swallowed so a
                          ledger problem never breaks a render
  scan(text)           -> list of problems (used by tests and `credits.py check`)
CLI: credits.py check [files...]   (default: assets/photos/CREDITS.csv + episodes/*/photo_credits.md) -> exit 1 on leaks
     credits.py sanitize            rewrite CREDITS.csv + every photo_credits.md through the whitelist"""
import csv, io, os, re, sys, tempfile
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ["date", "episode", "file", "public", "role", "title", "author", "credit", "source", "source_url", "license", "license_url", "verified_via", "width", "height"]
URL_FIELDS = {"source_url", "license_url"}
PATH_FIELDS = {"file", "public"}
_TOKENISH = re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|token|sig|signature|x-amz-[a-z-]+|key|auth|password|secret)=[^\s&#]+")
_LONG_SECRET = re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})")
_LOCAL_PATH = re.compile(r"(?:(?<![\w/])/(?:home|Users|workspace|tmp|var|root|mnt|private|cursor)/[^\s|,;)\]]*|[A-Za-z]:\\[^\s|,;)\]]*|~/[^\s|,;)\]]*)")
SAFE_QUERY = {"curid", "oldid"}
_URL_IN_TEXT = re.compile(r"[a-z][a-z0-9+.-]*://[^\s|)\]>]+", re.I)

def safe_public_url(value):
    if not isinstance(value, str) or not value.strip(): return None
    try: p = urlsplit(value.strip())
    except ValueError: return None
    if p.scheme not in ("http", "https") or not p.hostname or p.username is not None or p.password is not None: return None
    # stable public page identifiers survive (Commons "index.php?curid=N"); every other query param is dropped
    q = "&".join(kv for kv in p.query.split("&") if kv.split("=", 1)[0] in SAFE_QUERY and _TOKENISH.search(kv) is None)
    return urlunsplit((p.scheme, p.hostname + (f":{p.port}" if p.port else ""), p.path, q, ""))

def _scrub_text(v):
    v = _URL_IN_TEXT.sub(lambda m: safe_public_url(m.group(0)) or "[url removed]", str(v))
    v = _TOKENISH.sub("[redacted]", v); v = _LONG_SECRET.sub("[redacted]", v)
    return _LOCAL_PATH.sub("[local path removed]", v).strip()

def _safe_path(v):
    if not v: return ""
    p = Path(str(v))
    try: return str(p.resolve().relative_to(ROOT)) if p.is_absolute() else (str(p) if not str(p).startswith(("..", "~")) else p.name)
    except ValueError: return p.name

def credit_record(row):
    out = {}
    for k in FIELDS:
        v = row.get(k, "")
        if k in URL_FIELDS: v = safe_public_url(v) or ""
        elif k in PATH_FIELDS: v = _safe_path(v)
        elif k in ("width", "height"): v = int(v) if str(v).isdigit() else ""
        else: v = _scrub_text(v) if v is not None else ""
        out[k] = v
    return out

def scan(text):
    probs = []
    for m in _URL_IN_TEXT.finditer(text):
        u = m.group(0); s = safe_public_url(u)
        if s is None: probs.append(f"non-public url: {u[:40]}…")
        elif s != u.rstrip(".,;"): probs.append(f"url with query/fragment: {s}")
    if _TOKENISH.search(text) or _LONG_SECRET.search(text): probs.append("token-looking string")
    if _LOCAL_PATH.search(text): probs.append("local path")
    return probs

def _atomic_write(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    with os.fdopen(fd, "w", newline="") as f: f.write(data)
    os.replace(tmp, path)

def persist(rows, credits_csv, md_by_episode=None, log=print):
    """Write the ledger; never raises (a ledger failure must not break a render). Returns True on success."""
    try:
        rows = [credit_record(r) for r in rows]
        buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n"); w.writeheader(); w.writerows(rows)
        _atomic_write(credits_csv, buf.getvalue())
        for ep, md in (md_by_episode or {}).items():
            ep_rows = [r for r in rows if r["episode"] == ep]
            gen = [f"- {r['credit']} - {r['source_url']}" for r in ep_rows]
            # keep hand-written notes (e.g. a derivative-image note), scrubbed; drop stale/duplicate generated rows
            old = Path(md).read_text().splitlines()[1:] if Path(md).exists() else []
            notes = [_scrub_text(l) for l in old if l.strip() and l not in gen and not any(l.startswith(f"- {r['credit']} - ") for r in ep_rows)]
            lines = ["Photo credits (public domain / CC0, no attribution required; credited anyway):"] + gen + notes
            _atomic_write(md, "\n".join(lines) + "\n")
        return True
    except Exception as e:  # noqa: BLE001 - deliberate: ledger is auxiliary
        log(f"credits: ledger not persisted ({type(e).__name__}); render continues")
        return False

def _defaults():
    return [ROOT / "assets/photos/CREDITS.csv", *sorted(ROOT.glob("episodes/*/photo_credits.md"))]

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        bad = 0
        for f in [Path(x) for x in sys.argv[2:]] or _defaults():
            if not f.exists(): continue
            for p in scan(f.read_text()): print(f"LEAK {f.relative_to(ROOT) if f.is_absolute() else f}: {p}"); bad += 1
        print("credits check:", "FAIL" if bad else "PASS"); sys.exit(1 if bad else 0)
    if cmd == "sanitize":
        cp = ROOT / "assets/photos/CREDITS.csv"
        rows = list(csv.DictReader(open(cp))) if cp.exists() else []
        eps = {r["episode"]: ROOT / "episodes" / r["episode"] / "photo_credits.md" for r in rows}
        print("sanitized" if persist(rows, cp, eps) else "failed", len(rows), "rows")
