import sys
import uvicorn

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pydantic import BaseSettings


class Settings(BaseSettings):
    BASE_URL = "http://localhost:8000"
    USE_NGROK = True


BASE_DIR = str(Path(__file__).resolve().parent.parent)
settings = Settings()
app = FastAPI()


def init_webhooks(base_url):
    # Update inbound traffic via APIs to use the public-facing ngrok URL
    pass


if settings.USE_NGROK:
    from pyngrok import ngrok
    port = "8000"
    public_url = ngrok.connect(port).public_url
    settings.BASE_URL = public_url
    init_webhooks(public_url)
    print(public_url)


app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR + "\\static"),
    name="static",
)
templates = Jinja2Templates(directory=BASE_DIR + "\\templates")
chosen_values = {'cor': 'Норма, CN', 'pulm': 'Норма, LN'}
with open('python/patology.txt', 'r') as all_patologies:
    values = {}
    list_patologies = [i.replace('\n', '').split(',') for i in all_patologies.readlines()]
    for patology in list_patologies:
        if patology[-1] not in values.keys():
            values[patology[-1]] = [', '.join(patology[:-1])]
        else:
            values[patology[-1]].append(', '.join(patology[:-1]))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "chosen": chosen_values, "values": values}
    )


@app.post("/handle-change")
async def handle_change(request: Request):
    form_data = await request.form()
    chosen_values = dict(form_data)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "chosen": chosen_values, "values": values}
    )


@app.get("/current-values")
async def handle_valyes(request: Request):
    return chosen_values


uvicorn.run(app, host="localhost", port=8000)
