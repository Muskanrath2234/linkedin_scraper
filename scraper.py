from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time

app = FastAPI()


class LinkedInRequest(BaseModel):
    keyword: str
    sessioncookie: str
    max_posts: Optional[int] = None


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def authenticate_linkedin(driver, cookie):
    driver.get("https://www.linkedin.com/")
    time.sleep(3)
    driver.add_cookie({
        'name': 'li_at',
        'value': cookie,
        'domain': '.linkedin.com',
        'path': '/',
        'httpOnly': True,
        'secure': True
    })


@app.post("/scrape-linkedin")
def scrape_linkedin_posts(request: LinkedInRequest):
    driver = None
    try:
        driver = setup_driver()
        authenticate_linkedin(driver, request.sessioncookie)
        search_url = f"https://www.linkedin.com/search/results/content/?keywords={request.keyword.replace(' ', '%20')}&origin=SWITCH_SEARCH_VERTICAL"
        driver.get(search_url)
        time.sleep(5)

        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_posts = soup.find_all("div", class_="fie-impression-container")
        posts = all_posts if request.max_posts is None else all_posts[:request.max_posts]

        results = []

        for i, post in enumerate(posts, 1):
            try:
                name_element = post.find("span", class_="update-components-actor__title")
                name = name_element.get_text(strip=True) if name_element else "Unknown"

                post_element = driver.find_elements(By.CLASS_NAME, "fie-impression-container")[i - 1]
                profile_element = post_element.find_element(By.CSS_SELECTOR, "a[href*='/in/']")
                profile_url = profile_element.get_attribute("href").split('?')[0] if profile_element else "URL not available"

                content = post.find("div", class_="update-components-text")
                content_text = content.get_text(strip=True) if content else "No content available"

                results.append({
                    "post_number": i,
                    "name": name,
                    "profile_url": profile_url,
                    "content": content_text
                })
            except Exception as inner_error:
                results.append({
                    "post_number": i,
                    "error": f"Failed to extract post #{i}: {str(inner_error)}"
                })

        return {"status": "success", "keyword": request.keyword, "results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

    finally:
        if driver:
            driver.quit()
