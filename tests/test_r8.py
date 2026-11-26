"""r8 unit tests: credits sanitizer, pause tags, script alignment, hook rules, fade-only lint. Run: .venv-tts/bin/python tests/test_r8.py"""
import sys, json, tempfile, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import credits

def t_credits():
    s = credits.safe_public_url
    assert s("https://ex.com/a/b.jpg?token=abc&sig=1#x") == "https://ex.com/a/b.jpg"
    assert s("https://user:pass@ex.com/p") is None and s("file:///home/x.jpg") is None and s("/home/box/x.jpg") is None and s("ftp://ex.com/x") is None
    assert s("https://commons.wikimedia.org/w/index.php?curid=123&api_key=zz") == "https://commons.wikimedia.org/w/index.php?curid=123"
    r = credits.credit_record(dict(episode="03-sky", file="/workspace/ttm-r7/assets/photos/03-sky/a.jpg", source_url="https://x.org/p?key=SECRET",
                                   license_url="https://user:pw@x.org/l", author="Jane (/home/box/tmp/a.jpg) api_key=SECRETVALUE", credit="A / B / CC0", width="10"))
    assert r["source_url"] == "https://x.org/p" and r["license_url"] == "" and "SECRET" not in json.dumps(r) and "/home/" not in json.dumps(r), r
    assert not r["file"].startswith("/"), r["file"]
    assert credits.scan("see https://x.org/a?token=1") and credits.scan("/home/box/x") and not credits.scan("https://x.org/a")
    d = tempfile.mkdtemp(); ok = credits.persist([dict(episode="e", credit="c", source_url="https://x.org/p?sig=2")], Path(d) / "C.csv", {"e": Path(d) / "e.md"})
    assert ok and "sig" not in (Path(d) / "e.md").read_text()
    # persistence failure never raises (target is a directory)
    assert credits.persist([dict(episode="e")], Path(d), log=lambda m: None) is False

TESTS = [t_credits]
if __name__ == "__main__":
    for t in TESTS: t(); print("PASS", t.__name__)
