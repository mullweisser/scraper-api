from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, Schema
from starlette.middleware.cors import CORSMiddleware

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

class Request(BaseModel):
    url: str = Schema(None, title="The description of the item", max_length=1000)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def kill_chromedriver(browser):
    browser.quit()


@app.get("/")
def root():
    return {"status": "online"}


@app.post("/scrape/")
async def read_item(request: Request, background_tasks: BackgroundTasks):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('no-sandbox')
    options.add_argument('disable-gpu')
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    browser.get(request.url)
    background_tasks.add_task(kill_chromedriver, browser)
    return {
        "url": request.url,
        "content": browser.page_source
    }
