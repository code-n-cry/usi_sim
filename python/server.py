from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pathlib import Path

BASE_DIR = str(Path(__file__).resolve().parent.parent)
app = FastAPI()
app.mount(
    BASE_DIR + "/static",
    StaticFiles(directory=BASE_DIR + "/static"),
    name="static",
)
templates = Jinja2Templates(directory=BASE_DIR + "/templates")
chosen_values = {'Сердце': 'норма'}
values = {'Сердце': ['норма', 'порок 1', 'порок 2']}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "chosen": chosen_values, "values": values}
    )


@app.post("/handle-change")
async def handle_change(request: Request, value: str = Form(...)):
    chosen_values['Сердце'] = value
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "chosen": chosen_values, "values": values}
    )


@app.get("/current-values")
async def handle_valyes(request: Request):
    return chosen_values
