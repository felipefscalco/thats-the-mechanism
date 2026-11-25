#!/usr/bin/env python3
"""Licensed real-photo step: search ONLY public-domain / CC0 sources, verify each licence at the source, download, log credits.

Sources (each licence is re-read from the source's own API or page, never assumed):
  openverse  api.openverse.org  license=cc0,pdm  -> then re-verified on the item's landing page (or Commons API for Wikimedia items)
  commons    commons.wikimedia.org API extmetadata (LicenseShortName, Restrictions, Categories)
  nasa       images-api.nasa.gov (NASA media are not copyrighted unless a third-party credit is present -> rejected)
  loc        www.loc.gov JSON (only items whose rights text says "No known restrictions" / public domain / free to use)

Rejects: NC, ND, BY-SA, BY (needs attribution, kept out of v4 for simplicity), unknown licence, logos/trademarks,
identifiable people (Commons "personality" restriction, person keywords), tiny images (<900 px short side).
A human/bot still LOOKS at every picked image before use (people/logos in frame) - see skills/licensed-photos/SKILL.md.

Usage:
  photos.py search <slug> "<query>" [--sources openverse,commons,nasa,loc] [-n 8]   -> assets/photos/_candidates/<slug>.json (+ thumbs)
  photos.py pick <slug> <candidate_key> "<on-screen role>"                          -> assets/photos/<slug>/<file>, CREDITS.csv, episodes/<slug>/photo_credits.md
"""
import csv, html, json, re, sys, time, urllib.parse
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
PH = ROOT / "assets" / "photos"; CAND = PH / "_candidates"
UA = {"User-Agent": "ThatsTheMechanismPilot/0.4 (educational shorts; contact via repo) python-requests"}
OK_LIC = {"cc0", "pdm", "public domain", "pd", "pd-usgov", "pd-usgov-nasa", "no known restrictions"}
BAD = re.compile(r"\b(by-nc|nc-|noncommercial|by-nd|noderiv|by-sa|sharealike|all rights reserved)\b", re.I)
PEOPLE = re.compile(r"\b(portrait|selfie|man|woman|men|women|girl|boy|child|children|people|person|crowd|face|astronaut[s]? (posing|portrait)|crew portrait)\b", re.I)
LOGO = re.compile(r"\b(logo|logos|trademark|brand mark|wordmark|emblem)\b", re.I)
get = lambda url, **kw: requests.get(url, headers=UA, timeout=30, **kw)
strip = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()

def commons_info(title=None, pageid=None):
    sel = dict(pageids=pageid) if pageid else dict(titles=title)
    r = get("https://commons.wikimedia.org/w/api.php", params=dict(action="query", format="json", **sel, prop="imageinfo|categories",
            iiprop="url|extmetadata|size|mime", iiurlwidth=1600, cllimit=50)).json()
    p = next(iter(r["query"]["pages"].values()))
    if "imageinfo" not in p: return None
    ii = p["imageinfo"][0]; m = ii["extmetadata"]; v = lambda k: strip(m.get(k, {}).get("value", ""))
    cats = " ".join(c["title"] for c in p.get("categories", []))
    title = p["title"]
    return dict(key="commons:" + title, source="Wikimedia Commons", title=title.replace("File:", ""), page=ii["descriptionurl"],
                url=ii.get("thumburl") or ii["url"], orig=ii["url"], w=ii["width"], h=ii["height"], mime=ii["mime"],
                author=v("Artist") or "unknown", license=v("LicenseShortName"), license_url=v("LicenseUrl"),
                restrictions=v("Restrictions"), text=v("ImageDescription") + " " + cats, verified_via="Commons API extmetadata")

def verdict(c):
    lic = (c.get("license") or "").lower().strip(); why = []
    if not lic: why.append("no licence")
    elif BAD.search(lic) or BAD.search(c.get("license_url", "")): why.append(f"licence {c['license']} not allowed")
    elif not (lic in OK_LIC or lic.startswith("cc0") or lic.startswith("public domain") or lic.startswith("pd") or "publicdomain" in c.get("license_url", "")):
        why.append(f"licence {c['license']} is not PD/CC0")
    if re.search(r"personality|trademark|insignia", c.get("restrictions", ""), re.I): why.append("restriction: " + c["restrictions"][:60])
    t = c.get("title", "") + " " + c.get("text", "")
    if LOGO.search(t): why.append("logo/trademark keyword")
    if PEOPLE.search(t): why.append("people keyword (identifiable people risk)")
    deliver = c.get("url", "").lower().split("?")[0]
    if not deliver.endswith((".jpg", ".jpeg", ".png")): why.append(f"not a jpg/png delivery ({c.get('mime') or deliver[-5:]})")
    if min(c.get("w") or 0, c.get("h") or 0) < 900: why.append("too small")
    c["ok"], c["reject"] = not why, why
    return c

def s_commons(q, n):
    r = get("https://commons.wikimedia.org/w/api.php", params=dict(action="query", format="json", list="search", srnamespace=6, srsearch=q + " filetype:bitmap", srlimit=n)).json()
    return [x for x in (commons_info(h["title"]) for h in r["query"]["search"]) if x]

def s_openverse(q, n):
    r = get("https://api.openverse.org/v1/images/", params=dict(q=q, license="cc0,pdm", page_size=n, mature="false")).json()
    out = []
    for it in r.get("results", []):
        c = dict(key="openverse:" + it["id"], source=f"Openverse/{it['source']}", title=it["title"] or "", page=it["foreign_landing_url"], url=it["url"],
                 w=it.get("width") or 0, h=it.get("height") or 0, author=it.get("creator") or "unknown", license="", license_url="",
                 text=" ".join(t["name"] for t in it.get("tags") or []), openverse_license=f"{it['license']} {it['license_version']}")
        # verify at the source, not from the aggregator
        if "wikimedia" in it["source"] and ("/wiki/File:" in c["page"] or "curid=" in c["page"]):
            ci = commons_info(pageid=c["page"].split("curid=")[1]) if "curid=" in c["page"] else commons_info("File:" + urllib.parse.unquote(c["page"].split("/wiki/File:")[1]))
            if ci: ci["key"] = c["key"]; ci["openverse_license"] = c["openverse_license"]; out.append(ci); continue
        try:
            pg = get(c["page"]).text
            m = re.search(r"creativecommons\.org/(publicdomain/(zero|mark)/1\.0)", pg)
            if m: c["license"], c["license_url"] = ("CC0 1.0" if m.group(2) == "zero" else "Public Domain Mark 1.0"), "https://creativecommons.org/" + m.group(1) + "/"
            elif re.search(r"creativecommons\.org/licenses/[a-z-]+", pg): c["license"] = "CC licence on page: " + re.search(r"creativecommons\.org/licenses/([a-z-]+)", pg).group(1)
            c["verified_via"] = "landing page HTML licence link"
        except Exception as e: c["verified_via"] = f"landing page fetch failed: {e}"
        out.append(c)
    return out

def s_nasa(q, n):
    r = get("https://images-api.nasa.gov/search", params=dict(q=q, media_type="image")).json()
    out = []
    for it in r["collection"]["items"][:n]:
        d = it["data"][0]; nid = d["nasa_id"]
        files = get(f"https://images-api.nasa.gov/asset/{urllib.parse.quote(nid)}").json()["collection"]["items"]
        hrefs = [f["href"] for f in files if f["href"].lower().endswith((".jpg", ".jpeg", ".png"))]
        pick = next((h for h in hrefs if "~large" in h), next((h for h in hrefs if "~orig" in h), hrefs[0] if hrefs else ""))
        third = " ".join(filter(None, [d.get("photographer"), d.get("secondary_creator")]))
        credit_3p = bool(re.search(r"(©|copyright|courtesy of (?!nasa)|getty|reuters|ap photo)", (d.get("description", "") + " " + third), re.I))
        c = dict(key="nasa:" + nid, source="NASA Image and Video Library", title=d.get("title", ""), page=f"https://images.nasa.gov/details/{nid}", url=pick.replace(" ", "%20").replace("http://", "https://"),
                 w=0, h=0, author=third or f"NASA ({d.get('center', '')})", license="" if credit_3p else "Public domain (NASA media usage guidelines)",
                 license_url="https://www.nasa.gov/nasa-brand-center/images-and-media/", text=d.get("description", "")[:400] + " " + " ".join(d.get("keywords", [])),
                 verified_via="images-api.nasa.gov metadata (no third-party credit)" if not credit_3p else "third-party credit found -> rejected")
        out.append(c)
    return out

def s_loc(q, n):
    r = get("https://www.loc.gov/photos/", params={"q": q, "fo": "json", "c": n, "fa": "online-format:image"}).json()
    out = []
    for it in r.get("results", [])[:n]:
        rights = " ".join(it.get("rights_advisory", []) if isinstance(it.get("rights_advisory"), list) else [str(it.get("rights_advisory", ""))])
        if not rights:
            try: rights = " ".join(get(it["id"].rstrip("/") + "/?fo=json").json().get("item", {}).get("rights_advisory", []))
            except Exception: pass
        free = bool(re.search(r"no known restrictions|public domain|free to use", rights, re.I))
        imgs = it.get("image_url") or []
        out.append(dict(key="loc:" + it["id"].rstrip("/").split("/")[-1], source="Library of Congress", title=it.get("title", ""), page=it["id"],
                        url=(imgs[-1].split("#")[0] if imgs else ""), w=0, h=0, author=", ".join(it.get("contributor", []) or ["unknown"]),
                        license="No known restrictions (LOC rights advisory)" if free else "", license_url=it["id"], text=rights + " " + " ".join(it.get("subject", [])),
                        verified_via="loc.gov JSON rights_advisory"))
    return out

def fill_size(c):
    if c.get("w") and c.get("h") or not c.get("url"): return c
    try:
        from PIL import Image; import io
        im = Image.open(io.BytesIO(get(c["url"]).content)); c["w"], c["h"] = im.size
    except Exception: pass
    return c

def search(slug, q, sources, n):
    CAND.mkdir(parents=True, exist_ok=True)
    fn = dict(openverse=s_openverse, commons=s_commons, nasa=s_nasa, loc=s_loc)
    p = CAND / f"{slug}.json"; db = json.loads(p.read_text()) if p.exists() else {}
    for s in sources:
        try: res = fn[s](q, n)
        except Exception as e: print("source failed", s, e); continue
        for c in res:
            c = verdict(fill_size(c)); c["query"] = q; db[c["key"]] = c
            print(("OK  " if c["ok"] else "REJ ") + f"{c['key'][:60]:60s} {c['license'][:34]:34s} {c['w']}x{c['h']} {'; '.join(c['reject'])}")
    p.write_text(json.dumps(db, indent=1))

def pick(slug, key, role):
    db = json.loads((CAND / f"{slug}.json").read_text()); c = db[key]
    # re-verify at pick time (licences can change)
    if "commons.wikimedia.org" in c.get("page", ""):
        fresh = commons_info("File:" + c["page"].split("/wiki/File:")[1].replace("_", " ")) if "/wiki/File:" in c["page"] else commons_info(pageid=c["page"].split("curid=")[1])
        if fresh: c.update({k: fresh[k] for k in ("license", "license_url", "restrictions", "author")}); c["text"] = fresh["text"]
    c = verdict(c)
    if not c["ok"]: sys.exit(f"REJECTED at pick: {c['reject']}")
    d = PH / slug; d.mkdir(parents=True, exist_ok=True)
    ext = ".png" if c["url"].lower().split("?")[0].endswith(".png") else ".jpg"
    name = re.sub(r"[^a-z0-9]+", "-", (re.sub(r"\.(jpe?g|png|tiff?)$", "", c["title"], flags=re.I) or key).lower())[:50].strip("-") + ext
    data = get(c["url"]).content; (d / name).write_bytes(data)
    (ROOT / "remotion" / "public" / "photos").mkdir(parents=True, exist_ok=True); (ROOT / "remotion" / "public" / "photos" / f"{slug}--{name}").write_bytes(data)
    author = re.sub(r"\s+", " ", c["author"].split("\n")[0]).strip(" .")[:120]
    title = re.sub(r"\.(jpe?g|png|tiff?)$", "", c["title"], flags=re.I)
    short = (title[:70] + "...") if len(title) > 70 else title
    row = dict(date=time.strftime("%Y-%m-%d"), episode=slug, file=f"assets/photos/{slug}/{name}", public=f"photos/{slug}--{name}", role=role, title=title,
               author=author, credit=f"{short} / {author} / {c['license']}", source=c["source"], source_url=c["page"], license=c["license"], license_url=c.get("license_url") or c["page"], verified_via=c.get("verified_via", ""),
               width=c["w"], height=c["h"])
    cp = PH / "CREDITS.csv"; new = not cp.exists()
    rows = [] if new else [r for r in csv.DictReader(open(cp)) if r["file"] != row["file"]]
    rows.append(row)
    with open(cp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row)); w.writeheader(); w.writerows(rows)
    ep_rows = [r for r in rows if r["episode"] == slug]
    lines = ["Photo credits (public domain / CC0, no attribution required; credited anyway):"] + [f"- {r['credit']} - {r['source_url']}" for r in ep_rows]
    (ROOT / "episodes" / slug / "photo_credits.md").write_text("\n".join(lines) + "\n")
    print("picked", row["file"], row["license"], row["source_url"])

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "search":
        srcs = (a[a.index("--sources") + 1] if "--sources" in a else "openverse,commons,nasa,loc").split(",")
        n = int(a[a.index("-n") + 1]) if "-n" in a else 8
        search(a[1], a[2], srcs, n)
    elif a[0] == "pick": pick(a[1], a[2], a[3])
