from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, Schema
from starlette.middleware.cors import CORSMiddleware

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

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

def text_not_to_be(css_selector, prohibited_text):
    """Wait until the text of the element selected by css_selector is not prohibited_text."""
    def compare_text(driver):
        try:
            element_text = driver.find_element(By.CSS_SELECTOR, css_selector).text
            return element_text != prohibited_text
        except:
            # If the element is not found, we can consider the condition not met
            return False
    return compare_text

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

@app.post("/scrape/details/")
async def read_item_wait_for_text_change(request: Request, background_tasks: BackgroundTasks):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('no-sandbox')
    options.add_argument('disable-gpu')
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    browser.get(request.url)
    
    # Wait for the specific CSS selector's text to change from "{{objektNr}}"
    WebDriverWait(browser, 10).until(
        text_not_to_be("#centercolumn > div.l-container.table.m-contentarea > div > div > div.MarketVehicleSpotsDetailViewBlock > div.fast2-widget.objectinfovehicles.objectinfoFORDON > div > dl > dd.ObjektNummer", "{{objektNr}}")
    )
    
    background_tasks.add_task(kill_chromedriver, browser)
    return {
        "url": request.url,
        "content": browser.page_source
    }
