#!/usr/bin/env python3
import os, json, time

PDF_DIR = "/srv/class-pdf/pdfs"
SITE_DIR = "/srv/class-pdf/site"
OUT = os.path.join(SITE_DIR, "index.json")

items = []
for dp, dn, fn in os.walk(PDF_DIR):
    for f in fn:
        if not f.lower().endswith(".pdf"):
            continue
        full = os.path.join(dp, f)
        rel = full.replace(PDF_DIR, "/pdfs").replace("\\", "/")
        try:
            mt = int(os.path.getmtime(full))
        except Exception:
            mt = 0
        rdir = os.path.relpath(dp, PDF_DIR)
        label = f if rdir == "." else f"{rdir}/{f}"
        items.append({"path": rel, "name": label, "mtime": mt})

items.sort(key=lambda x: x["mtime"], reverse=True)
data = {"generated_at": int(time.time()), "items": items}
os.makedirs(SITE_DIR, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fp:
    json.dump(data, fp, ensure_ascii=False)
print(f"Wrote {OUT} with {len(items)} items.")