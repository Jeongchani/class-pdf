from flask import Flask, request, jsonify, abort
from werkzeug.utils import secure_filename
import os, pathlib

app = Flask(__name__)

PDF_DIR = "/srv/class-pdf/pdfs"

def secure_path(subpath: str) -> pathlib.Path:
    subpath = (subpath or "").lstrip("/\\")
    base = pathlib.Path(PDF_DIR).resolve()
    p = (base / subpath).resolve()
    if str(p) != str(base) and not str(p).startswith(str(base) + os.sep):
        abort(400, description="invalid path")
    return p

@app.get("/health")
def health():
    return "ok", 200

@app.post("/upload")
def upload():
    if "file" not in request.files:
        return jsonify(error="no file"), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify(error="empty filename"), 400
    if not f.filename.lower().endswith(".pdf"):
        return jsonify(error="only .pdf allowed"), 400

    subdir = request.form.get("subdir", "").strip().strip("/\\")
    filename = secure_filename(f.filename)

    target_dir = secure_path(subdir)
    os.makedirs(target_dir, exist_ok=True)

    out_path = target_dir / filename
    f.save(str(out_path))
    try:
        os.chmod(out_path, 0o644)
    except Exception:
        pass

    web_path = str(out_path).replace(PDF_DIR, "/pdfs").replace("\\", "/")
    return jsonify(ok=True, path=web_path), 200

@app.post("/delete")
def delete():
    data = request.get_json(silent=True) or {}
    path = data.get("path") or request.args.get("path")
    if not path:
        return jsonify(error="missing path"), 400
    if not path.startswith("/pdfs/"):
        return jsonify(error="path must start with /pdfs/"), 400

    rel = path[len("/pdfs/"):]
    target = secure_path(rel)

    if not target.exists():
        return jsonify(error="not found"), 404

    if target.is_dir():
        try:
            os.rmdir(target)
            kind = "dir"
        except OSError:
            return jsonify(error="dir not empty"), 400
    else:
        target.unlink()
        kind = "file"

    return jsonify(ok=True, deleted=kind, path=path), 200