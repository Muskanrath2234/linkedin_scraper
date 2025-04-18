import os
import time
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from dataclasses import dataclass
from time import sleep
import pandas as pd

app = FastAPI(title="LinkedIn Profile Scraper API",
              description="API for scraping LinkedIn profile information")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Data classes (same as your original code)
@dataclass
class ContactInfo:
    email: str = None
    phone: str = None
    profile_url: str = None
    websites: list = None
    twitter: str = None
    birthday: str = None
    im: str = None
    address: str = None


@dataclass
class Institution:
    institution_name: str = None
    linkedin_url: str = None
    website: str = None
    industry: str = None
    type: str = None
    headquarters: str = None
    company_size: int = None
    founded: int = None


@dataclass
class Experience(Institution):
    from_date: str = None
    to_date: str = None
    description: str = None
    position_title: str = None
    duration: str = None
    location: str = None


@dataclass
class Education(Institution):
    from_date: str = None
    to_date: str = None
    description: str = None
    degree: str = None


@dataclass
class Interest(Institution):
    title: str = None


@dataclass
class Accomplishment(Institution):
    category: str = None
    title: str = None


class Scraper:
    def __init__(self, driver=None):
        self.driver = driver if driver else self._get_driver()
        self.WAIT_FOR_ELEMENT_TIMEOUT = 5
        self.TOP_CARD = "pv-top-card"

    # def _get_driver(self):
    #     options = webdriver.ChromeOptions()
    #     options.add_argument("--headless")  # Run in headless mode for server
    #     options.add_argument("--no-sandbox")
    #     options.add_argument("--disable-dev-shm-usage")
    #     options.add_argument("--start-maximized")
    #     options.add_argument("--disable-blink-features=AutomationControlled")
    #     options.add_experimental_option("excludeSwitches", ["enable-automation"])
    #     options.add_experimental_option('useAutomationExtension', False)

    #     try:
    #         # Check if CHROMEDRIVER env var is set, otherwise use hardcoded path,replace with your chrome path
    #         driver_path = os.getenv("CHROMEDRIVER", "C:/Users/DELL/Downloads/chromedriver-win64/chromedriver.exe")

    #         # Use Service object as per latest Selenium standards
    #         service = Service(driver_path)
    #         return webdriver.Chrome(service=service, options=options)
    #     except Exception as e:
    #         print(f"[Error] Failed to initialize Chrome WebDriver: {e}")
    #         raise
#automaticly handle chrome
  import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def _get_driver(self):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Headless mode for server environments
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    try:
        # Automatically installs and sets up the appropriate chromedriver
        driver_path = chromedriver_autoinstaller.install()

        # Create a Service object with the installed chromedriver path
        service = Service(driver_path)

        # Initialize Chrome WebDriver with service and options
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    except Exception as e:
        print(f"[Error] Failed to initialize Chrome WebDriver: {e}")
        raise


    @staticmethod
    def wait(duration):
        sleep(int(duration))

    def focus(self):
        self.driver.execute_script('alert("Focus window")')
        self.driver.switch_to.alert.accept()

    def mouse_click(self, elem):
        action = webdriver.ActionChains(self.driver)
        action.move_to_element(elem).perform()

    def wait_for_element_to_load(self, by=By.CLASS_NAME, name="pv-top-card", base=None):
        base = base or self.driver

        try:
            return WebDriverWait(base, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((by, name))
            )
        except TimeoutException:
            print(f"[Timeout] Element '{name}' not found using {by} within {self.WAIT_FOR_ELEMENT_TIMEOUT} seconds.")
            return None

    def wait_for_all_elements_to_load(self, by=By.CLASS_NAME, name="pv-top-card", base=None):
        base = base or self.driver
        return WebDriverWait(base, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_all_elements_located((by, name)))

    def is_signed_in(self):
        try:
            self.driver.find_element(By.CLASS_NAME, "global-nav__me")
            return True
        except:
            try:
                self.driver.find_element(By.CLASS_NAME, "nav__button-secondary")
                return False
            except:
                return False

    def scroll_to_half(self):
        self.driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));")

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scroll_class_name_element_to_page_percent(self, class_name: str, page_percent: float):
        self.driver.execute_script(
            f'elem = document.getElementsByClassName("{class_name}")[0]; elem.scrollTo(0, elem.scrollHeight*{str(page_percent)});'
        )

    def __find_element_by_class_name__(self, class_name):
        try:
            self.driver.find_element(By.CLASS_NAME, class_name)
            return True
        except:
            return False

    def __find_element_by_xpath__(self, tag_name):
        try:
            self.driver.find_element(By.XPATH, tag_name)
            return True
        except:
            return False

    def __find_enabled_element_by_xpath__(self, tag_name):
        try:
            elem = self.driver.find_element(By.XPATH, tag_name)
            return elem.is_enabled()
        except:
            return False

    @classmethod
    def __find_first_available_element__(cls, *args):
        for elem in args:
            if elem:
                return elem[0]


class Person(Scraper):
    __TOP_CARD = "main"
    __WAIT_FOR_ELEMENT_TIMEOUT = 5

    def __init__(
            self,
            linkedin_url=None,
            name=None,
            about=None,
            experiences=None,
            educations=None,
            interests=None,
            accomplishments=None,
            company=None,
            job_title=None,
            contacts=None,
            driver=None,
            get=True,
            scrape=True,
            close_on_complete=True,
            time_to_wait_after_login=0,
            cookies=None,
    ):
        self.linkedin_url = linkedin_url
        self.name = name
        self.about = about or []
        self.experiences = experiences or []
        self.educations = educations or []
        self.interests = interests or []
        self.accomplishments = accomplishments or []
        self.also_viewed_urls = []
        self.contacts = contacts or []
        self.cookies = cookies
        self.location = None
        self.open_to_work = False

        super().__init__(driver)

        if get:
            if self.cookies:
                self.driver.get("https://www.linkedin.com")
                for cookie in self.cookies:
                    self.driver.add_cookie(cookie)
                self.driver.get(linkedin_url)
            else:
                self.driver.get(linkedin_url)

        if scrape:
            self.scrape(close_on_complete)

    def add_experience(self, experience):
        self.experiences.append(experience)

    def add_education(self, education):
        self.educations.append(education)

    def add_interest(self, interest):
        self.interests.append(interest)

    def add_accomplishment(self, accomplishment):
        self.accomplishments.append(accomplishment)

    def add_contact(self, contact):
        self.contacts.append(contact)

    def scrape(self, close_on_complete=True):
        if self.is_signed_in():
            self.scrape_logged_in(close_on_complete=close_on_complete)
        else:
            print("You are not logged in!")

    def _click_see_more_by_class_name(self, class_name):
        try:
            _ = self.wait_for_element_to_load(By.CLASS_NAME, class_name)
            div = self.driver.find_element(By.CLASS_NAME, class_name)
            div.find_element(By.TAG_NAME, "button").click()
        except Exception as e:
            pass

    def is_open_to_work(self):
        try:
            return "#OPEN_TO_WORK" in self.driver.find_element(By.CLASS_NAME,
                                                               "pv-top-card-profile-picture").find_element(By.TAG_NAME,
                                                                                                           "img").get_attribute(
                "title")
        except:
            return False

    def get_experiences(self):
        url = f"{self.linkedin_url}/details/experience/"
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()

        try:
            main_list = self.wait_for_element_to_load(name="pvs-list__container", base=main)
        except TimeoutException:
            return

        for position in main_list.find_elements(By.CLASS_NAME, "pvs-list__paged-list-item"):
            try:
                position = position.find_element(By.CSS_SELECTOR, "div[data-view-name='profile-component-entity']")
                company_logo_elem, position_details = position.find_elements(By.XPATH, "*")

                # company elem
                company_linkedin_url = company_logo_elem.find_element(By.XPATH, "*").get_attribute("href")
                if not company_linkedin_url:
                    continue

                # position details
                position_details_list = position_details.find_elements(By.XPATH, "*")
                position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
                position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
                outer_positions = position_summary_details.find_element(By.XPATH, "*").find_elements(By.XPATH, "*")

                if len(outer_positions) == 4:
                    position_title = outer_positions[0].find_element(By.TAG_NAME, "span").text
                    company = outer_positions[1].find_element(By.TAG_NAME, "span").text
                    work_times = outer_positions[2].find_element(By.TAG_NAME, "span").text
                    location = outer_positions[3].find_element(By.TAG_NAME, "span").text
                elif len(outer_positions) == 3:
                    if "·" in outer_positions[2].text:
                        position_title = outer_positions[0].find_element(By.TAG_NAME, "span").text
                        company = outer_positions[1].find_element(By.TAG_NAME, "span").text
                        work_times = outer_positions[2].find_element(By.TAG_NAME, "span").text
                        location = ""
                    else:
                        position_title = ""
                        company = outer_positions[0].find_element(By.TAG_NAME, "span").text
                        work_times = outer_positions[1].find_element(By.TAG_NAME, "span").text
                        location = outer_positions[2].find_element(By.TAG_NAME, "span").text
                else:
                    position_title = ""
                    company = outer_positions[0].find_element(By.TAG_NAME, "span").text
                    work_times = ""
                    location = ""

                times = work_times.split("·")[0].strip() if work_times else ""
                duration = work_times.split("·")[1].strip() if len(work_times.split("·")) > 1 else None

                from_date = " ".join(times.split(" ")[:2]) if times else ""
                to_date = " ".join(times.split(" ")[3:]) if times else ""

                description = ""
                if position_summary_text:
                    if any(element.get_attribute("class") == "pvs-list__container" for element in
                           position_summary_text.find_elements(By.TAG_NAME, "*")):
                        inner_positions = position_summary_text.find_element(By.CLASS_NAME, "pvs-list__container") \
                            .find_element(By.XPATH, "*").find_element(By.XPATH, "*").find_element(By.XPATH, "*") \
                            .find_elements(By.CLASS_NAME, "pvs-list__paged-list-item")
                        for desc in inner_positions:
                            description += desc.text + "\n"
                    else:
                        description = position_summary_text.text

                experience = Experience(
                    position_title=position_title,
                    from_date=from_date,
                    to_date=to_date,
                    duration=duration,
                    location=location,
                    description=description,
                    institution_name=company,
                    linkedin_url=company_linkedin_url
                )
                self.add_experience(experience)
            except Exception as e:
                continue

    def get_about(self):
        try:
            about_section = self.driver.find_element(By.ID, "about")
            about = about_section.find_element(By.XPATH, "..").find_element(By.CSS_SELECTOR,
                                                                            "div.display-flex.ph5.pv3").text
            self.about = about
        except NoSuchElementException:
            self.about = None

    def get_contact_info(self):
        """Scrape contact information from LinkedIn profile using Selenium"""
        url = f"{self.linkedin_url}/overlay/contact-info/"
        print(f"Navigating to: {url}")

        try:
            self.driver.get(url)
            time.sleep(3)  # Allow page to load

            contact_info = ContactInfo()

            sections = self.driver.find_elements(By.CLASS_NAME, "pv-contact-info__contact-type")
            print(f"Found {len(sections)} contact info sections")

            for section in sections:
                try:
                    header = section.find_element(By.CLASS_NAME, "pv-contact-info__header").text.strip().lower()

                    if "email" in header:
                        email_elem = section.find_element(By.CSS_SELECTOR, "a[href^='mailto:']")
                        contact_info.email = email_elem.text.strip()
                    elif "phone" in header:
                        phone_elem = section.find_element(By.CLASS_NAME, "t-14")
                        contact_info.phone = phone_elem.text.strip()
                    elif "your profile" in header or "linkedin" in header:
                        profile_elem = section.find_element(By.CSS_SELECTOR, "a[href*='linkedin.com/in/']")
                        contact_info.profile_url = profile_elem.get_attribute("href")
                    elif "website" in header:
                        website_elems = section.find_elements(By.TAG_NAME, "a")
                        contact_info.websites = [a.get_attribute("href") for a in website_elems]
                    elif "twitter" in header:
                        twitter_elem = section.find_element(By.TAG_NAME, "a")
                        contact_info.twitter = twitter_elem.get_attribute("href")
                    elif "address" in header:
                        contact_info.address = section.text.strip()

                except Exception as e:
                    print(f"Error parsing section: {e}")
                    continue

            print(f"Scraped Contact Info: {contact_info}")
            return contact_info

        except Exception as e:
            print(f"Error fetching contact info: {e}")
            return None

    def get_educations(self):
        url = f"{self.linkedin_url}/details/education/"
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()

        try:
            main_list = self.wait_for_element_to_load(name="pvs-list__container", base=main)
        except TimeoutException:
            return

        for position in main_list.find_elements(By.CLASS_NAME, "pvs-list__paged-list-item"):
            try:
                position = position.find_element(By.CSS_SELECTOR, "div[data-view-name='profile-component-entity']")
                institution_logo_elem, position_details = position.find_elements(By.XPATH, "*")

                # institution elem
                institution_linkedin_url = institution_logo_elem.find_element(By.XPATH, "*").get_attribute("href")

                # position details
                position_details_list = position_details.find_elements(By.XPATH, "*")
                position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
                position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
                outer_positions = position_summary_details.find_element(By.XPATH, "*").find_elements(By.XPATH, "*")

                institution_name = outer_positions[0].find_element(By.TAG_NAME, "span").text
                if len(outer_positions) > 1:
                    degree = outer_positions[1].find_element(By.TAG_NAME, "span").text
                else:
                    degree = None

                if len(outer_positions) > 2:
                    times = outer_positions[2].find_element(By.TAG_NAME, "span").text

                    if times != "":
                        if "-" in times:
                            from_date = times.split(" ")[times.split(" ").index("-") - 1] if len(
                                times.split(" ")) > 3 else times.split(" ")[0]
                            to_date = times.split(" ")[-1]
                        else:
                            from_date = times
                            to_date = None
                else:
                    from_date = None
                    to_date = None

                description = position_summary_text.text if position_summary_text else ""

                education = Education(
                    from_date=from_date,
                    to_date=to_date,
                    description=description,
                    degree=degree,
                    institution_name=institution_name,
                    linkedin_url=institution_linkedin_url
                )
                self.add_education(education)
            except Exception as e:
                continue

    def get_name_and_location(self):
        try:
            top_panel = self.driver.find_element(By.CLASS_NAME, "mt2.relative")
            self.name = top_panel.find_element(By.TAG_NAME, "h1").text
            self.location = top_panel.find_element(By.CSS_SELECTOR,
                                                   "span.text-body-small.inline.t-black--light.break-words").text
        except Exception as e:
            print(f"Error getting name and location: {e}")

    def get_about(self):
        try:
            about_section = self.driver.find_element(By.ID, "about")
            about = about_section.find_element(By.XPATH, "..").find_element(By.CSS_SELECTOR,
                                                                            "div.display-flex.ph5.pv3").text
            self.about = about
        except NoSuchElementException:
            self.about = None

    def scrape_logged_in(self, close_on_complete=True):
        self.focus()
        self.wait(5)

        # get name and location
        self.get_name_and_location()
        self.open_to_work = self.is_open_to_work()

        # get about
        self.get_about()
        self.driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));")
        self.driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/1.5));")

        # get experience
        self.get_experiences()

        # get education
        self.get_educations()

        self.driver.get(self.linkedin_url)
        # get contact info
        contact_info = self.get_contact_info()
        if contact_info:
            self.contacts.append(contact_info)
        # get interest
        try:
            interestContainer = self.wait_for_element_to_load(
                By.XPATH,
                "//section[contains(@class, 'pv-interests-section')]"
            )
            for interestElement in interestContainer.find_elements(By.XPATH,
                                                                   ".//li[contains(@class, 'pv-interest-entity')]"
                                                                   ):
                interest = Interest(
                    interestElement.find_element(By.TAG_NAME, "h3").text.strip()
                )
                self.interests.append(interest)
        except Exception as e:
            pass

        # get accomplishment
        try:
            acc = self.wait_for_element_to_load(
                By.XPATH,
                "//section[contains(@class, 'pv-accomplishments-section')]"
            )
            for block in acc.find_elements(By.XPATH,
                                           ".//div[contains(@class, 'pv-accomplishments-block__content')]"
                                           ):
                category = block.find_element(By.TAG_NAME, "h3").text
                for title in block.find_element(By.TAG_NAME, "ul").find_elements(By.TAG_NAME, "li"):
                    accomplishment = Accomplishment(category, title.text)
                    self.accomplishments.append(accomplishment)
        except Exception as e:
            pass

        # get connections
        try:
            self.driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
            connections = self.wait_for_element_to_load(By.CLASS_NAME, "mn-connections")
            if connections is not None:
                for conn in connections.find_elements(By.CLASS_NAME, "mn-connection-card"):
                    anchor = conn.find_element(By.CLASS_NAME, "mn-connection-card__link")
                    url = anchor.get_attribute("href")
                    name = conn.find_element(By.CLASS_NAME, "mn-connection-card__name").text.strip()
                    occupation = conn.find_element(By.CLASS_NAME, "mn-connection-card__occupation").text.strip()

                    contact = ContactInfo(name=name, occupation=occupation, url=url)
                    self.contacts.append(contact)
        except Exception as e:
            pass

        if close_on_complete:
            self.driver.quit()

    @property
    def company(self):
        if self.experiences:
            return (
                self.experiences[0].institution_name
                if self.experiences[0].institution_name
                else None
            )
        else:
            return None

    @property
    def job_title(self):
        if self.experiences:
            return (
                self.experiences[0].position_title
                if self.experiences[0].position_title
                else None
            )
        else:
            return None

    def to_dict(self):
        """Convert scraped data to dictionary"""
        return {
            'basic_info': {
                'name': self.name,
                'about': self.about,
                'location': self.location,
                'open_to_work': self.open_to_work,
                'profile_url': self.linkedin_url
            },
            'contact_info': {
                'email': self.contacts[0].email if self.contacts else None,
                'phone': self.contacts[0].phone if self.contacts else None,
                'profile_url': self.contacts[0].profile_url if self.contacts else None,
                'twitter': self.contacts[0].twitter if self.contacts else None,
                'address': self.contacts[0].address if self.contacts else None,
                'websites': self.contacts[0].websites if self.contacts else None
            },
            'experiences': [{
                'position': exp.position_title,
                'company': exp.institution_name,
                'duration': exp.duration,
                'location': exp.location,
                'description': exp.description,
                'from_date': exp.from_date,
                'to_date': exp.to_date,
                'company_url': exp.linkedin_url
            } for exp in self.experiences],
            'educations': [{
                'institution': edu.institution_name,
                'degree': edu.degree,
                'from_date': edu.from_date,
                'to_date': edu.to_date,
                'description': edu.description,
                'institution_url': edu.linkedin_url
            } for edu in self.educations],
            'interests': [{
                'interest': interest.title
            } for interest in self.interests],
            'accomplishments': [{
                'category': acc.category,
                'title': acc.title
            } for acc in self.accomplishments]
        }


# Pydantic models for API request/response
class ProfileRequest(BaseModel):
    linkedin_url: str
    li_at_cookie: Optional[str] = None


class ProfileResponse(BaseModel):
    basic_info: Dict[str, Any]
    contact_info: Dict[str, Any]
    experiences: List[Dict[str, Any]]
    educations: List[Dict[str, Any]]
    interests: List[Dict[str, Any]]
    accomplishments: List[Dict[str, Any]]
    success: bool
    message: Optional[str] = None


@app.post("/search-profile", response_model=ProfileResponse, summary="Search LinkedIn Profile")
async def search_profile(request: ProfileRequest):
    """
    Search and scrape LinkedIn profile information based on the provided URL.

    Parameters:
    - linkedin_url: Valid LinkedIn profile URL (e.g., https://www.linkedin.com/in/username/)
    - li_at_cookie: (Optional) LinkedIn authentication cookie for accessing private profiles

    Returns:
    - Complete profile information including contact details, experiences, education, etc.
    """
    try:
        # Prepare cookies
        cookies = []
        if request.li_at_cookie:
            cookies.append({
                'name': 'li_at',
                'value': request.li_at_cookie,
                'domain': '.linkedin.com',
                'path': '/',
                'secure': True,
                'httpOnly': True
            })

        # Initialize scraper
        person = Person(
            linkedin_url=request.linkedin_url,
            cookies=cookies if cookies else None,
            scrape=True,
            close_on_complete=True
        )

        # Convert to dictionary
        profile_data = person.to_dict()

        return {
            **profile_data,
            "success": True,
            "message": "Profile information extracted successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"An error occurred: {str(e)}",
                "basic_info": {},
                "contact_info": {},
                "experiences": [],
                "educations": [],
                "interests": [],
                "accomplishments": []
            }
        )


@app.get("/")
async def root():
    return {
        "message": "LinkedIn Profile Scraper API",
        "endpoints": {
            "/search-profile": {
                "method": "POST",
                "description": "Search LinkedIn profile and return scraped data",
                "request_body": {
                    "linkedin_url": "string (required)",
                    "li_at_cookie": "string (optional)"
                }
            }
        }
    }
