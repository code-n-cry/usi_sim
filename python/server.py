from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
import shutil

app = FastAPI()

# Теперь server.py лежит в python/, а BASE_DIR — это корень проекта (папка-родитель папки python)
BASE_DIR   = Path(__file__).resolve().parent.parent
STORAGE    = BASE_DIR / "storage"
TEMPLATES  = BASE_DIR / "templates"

# Создаем storage, если его нет
STORAGE.mkdir(parents=True, exist_ok=True)

# Шаблоны из ../templates
templates = Jinja2Templates(directory=str(TEMPLATES))

# Раздаем загруженные видео из ../storage
app.mount("/storage", StaticFiles(directory=str(STORAGE)), name="storage")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

class LabelIn(BaseModel):
    number: str
    code: str

class NameIn(BaseModel):
    name: str

class RenameIn(BaseModel):
    newName: str

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/data")
async def list_all():
    out = []
    for lbl in sorted(STORAGE.iterdir()):
        if not lbl.is_dir(): continue
        pats = []
        for pat in sorted(lbl.iterdir()):
            if not pat.is_dir(): continue
            vids = [
                f"/storage/{lbl.name}/{pat.name}/{f.name}"
                for f in sorted(pat.iterdir())
                if f.is_file()
            ]
            pats.append({"name": pat.name, "files": vids})
        out.append({"name": lbl.name, "pathologies": pats})
    return out

@app.post("/api/labels", status_code=201)
async def create_label(in_: LabelIn):
    (STORAGE / f"{in_.number}_{in_.code}").mkdir(exist_ok=True)
    return {"ok": True}

@app.put("/api/labels/{label}/number")
async def rename_number(label: str, in_: RenameIn):
    num, code = label.split("_", 1)
    src = STORAGE / label
    dst = STORAGE / f"{in_.newName}_{code}"
    src.rename(dst)
    return {"ok": True}

@app.put("/api/labels/{label}/code")
async def rename_code(label: str, in_: RenameIn):
    num, code = label.split("_", 1)
    src = STORAGE / label
    dst = STORAGE / f"{num}_{in_.newName}"
    src.rename(dst)
    return {"ok": True}

@app.delete("/api/labels/{label}")
async def delete_label(label: str):
    shutil.rmtree(STORAGE / label, ignore_errors=True)
    return {"ok": True}

@app.post("/api/labels/{label}/pathologies", status_code=201)
async def create_pathology(label: str, in_: NameIn):
    (STORAGE / label / in_.name).mkdir(parents=True, exist_ok=True)
    return {"ok": True}

@app.put("/api/labels/{label}/pathologies/{pat}")
async def rename_pathology(label: str, pat: str, in_: RenameIn):
    src = STORAGE / label / pat
    dst = STORAGE / label / in_.newName
    src.rename(dst)
    return {"ok": True}

@app.delete("/api/labels/{label}/pathologies/{pat}")
async def delete_pathology(label: str, pat: str):
    shutil.rmtree(STORAGE / label / pat, ignore_errors=True)
    return {"ok": True}

@app.post(
    "/api/labels/{label}/pathologies/{pat}/files",
    status_code=201
)
async def upload_videos(
        label: str,
        pat: str,
        files: list[UploadFile] = File(...)
):
    dest_dir = STORAGE / label / pat
    for file in files:
        out_path = dest_dir / file.filename
        with out_path.open("wb") as buf:
            shutil.copyfileobj(file.file, buf)
    return {"ok": True}
