from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Schema, SecretStr
from starlette.middleware.cors import CORSMiddleware

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

app = FastAPI()

class Request(BaseModel):
    url: str = Schema(None, title="The description of the item", max_length=1000)

class LoginRequest(BaseModel):
    url: str
    username: str
    password: SecretStr  # Use SecretStr to ensure that the password is not printed in logs

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
    WebDriverWait(browser, 20).until(
        text_not_to_be("#centercolumn > div.l-container.table.m-contentarea > div > div > div.MarketVehicleSpotsDetailViewBlock > div.fast2-widget.objectinfovehicles.objectinfoFORDON > div > dl > dd.ObjektNummer", "{{objektNr}}")
    )
    
    background_tasks.add_task(kill_chromedriver, browser)
    return {
        "url": request.url,
        "content": browser.page_source
    }

@app.post("/login/stena/")
async def login(request: LoginRequest, background_tasks: BackgroundTasks):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('no-sandbox')
    options.add_argument('disable-gpu')
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
    try:
        print(f"URL: {request.url}")
        browser.get(request.url)
        browser.find_element(By.CSS_SELECTOR, "#tab3 > .apitext-loaded").click()
        username_input = browser.find_element(By.ID, "Username")
        password_input = browser.find_element(By.ID, "Password")
        login_button = browser.find_element(By.NAME, "button")
        apartments_list_button = browser.find_element(By.CSS_SELECTOR, ".mb-6:nth-child(2) > .group:nth-child(1) > .group > .truncate").click()
        
        print(f'Username: {request.username}')
        username_input.click()
        username_input.click()
        username_input.send_keys(request.username)
        
        password_input.click()
        password_input.click()
        password_input.send_keys(request.password.get_secret_value())
        login_button.click()
        apartments_list_button.click()

        # Optionally wait for some condition to verify login success
        # Example: WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "some-element-id")))
        # Extracting token from local storage
        token = browser.execute_script("return localStorage.getItem('token');")
        print("Your Bearer token is:", token)

        # Extracting token from a cookie
        cookie = browser.get_cookie('name_of_the_token_cookie')
        print("Your Bearer token is:", cookie['value'])

    except Exception as e:
        browser.quit()
        raise HTTPException(status_code=500, detail=str(e))

    background_tasks.add_task(kill_chromedriver, browser)
    
    return {"status": "Attempted login"}
