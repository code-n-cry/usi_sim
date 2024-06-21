import qrcode

from fastapi import FastAPI, Request
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
    pass


if settings.USE_NGROK:
    from pyngrok import ngrok
    port = "8000"
    public_url = ngrok.connect(port).public_url
    settings.BASE_URL = public_url
    init_webhooks(public_url)
    qr = qrcode.make(public_url)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR + "/static"),
    name="static",
)
templates = Jinja2Templates(directory=BASE_DIR + "/templates")
chosen_values = {
    '1': 'Норма, LN',
    '2': 'Норма, LN',
    '3': 'Норма, CN',
    '4': 'Норма, CN',
    '5': 'Норма, LN',
    '6': 'Норма, CN',
    '7': 'Норма, LN',
}
with open('patology.txt', 'r') as all_patologies:
    values = {}
    list_patologies = [
        i.replace('\n', '').split(',') for i in all_patologies.readlines()
    ]
    for patology in list_patologies:
        if patology[-1] not in values.keys():
            values[patology[-1]] = [', '.join(patology[:-1])]
        else:
            values[patology[-1]].append(', '.join(patology[:-1]))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "chosen": chosen_values, "values": values},
    )


@app.post("/handle-change")
async def handle_change(request: Request):
    global chosen_values
    form_data = await request.form()
    for i in dict(form_data):
        if i == '3':
            chosen_values['3'] = form_data[i]
            chosen_values['4'] = form_data[i]
            chosen_values['6'] = form_data[i]
        else:
            chosen_values[i] = form_data[i]
    print(dict(form_data), chosen_values)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "chosen": chosen_values, "values": values},
    )


@app.get("/current-values")
async def handle_valyes(request: Request):
    global chosen_values
    return chosen_values


qr.show()
