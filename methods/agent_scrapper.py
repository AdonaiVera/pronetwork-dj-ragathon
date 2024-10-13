from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from methods.linkedin_api.linkedin import Linkedin
import requests 

from dotenv import load_dotenv, find_dotenv
import os

_ = load_dotenv(find_dotenv()) 

KEY_LINKEDIN = os.environ['KEY_LINKEDIN']

KEY_LINKEDIN_PROFILE= os.environ['KEY_LINKEDIN']

def scrape_guests_from_event(url):
    # Initialize Safari WebDriver (you can use any driver)
    driver = webdriver.Safari()

    # Open the base page so the driver starts
    driver.get("https://lu.ma")

    # Add login cookies manually (after extracting from your browser)
    cookies = [
        {
            'name': 'luma.auth-session-key', 
            'value': KEY_LINKEDIN_PROFILE, 
            'domain': '.lu.ma',
            'path': '/',
        },
    ]

    for cookie in cookies:
        driver.add_cookie(cookie)

    # Now open the desired page after adding the cookies
    driver.get(url)

    # Wait for the page to load completely
    time.sleep(5)

    # Step 1: Simulate the click on the "257 Guests" button (or similar button for attendees)
    try:
        # Replace with the correct XPath/CSS selector for the "257 Guests" button
        guests_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "guests-button"))
        )
        guests_button.click()
        print("Guests button clicked successfully!")
    except Exception as e:
        print(f"Error clicking the guests button: {e}")
        driver.quit()
        return []

    # Step 2: Wait for the modal that contains the guest list to appear
    try:
        # Wait for the modal that contains the guest list to appear (adjust based on the structure)
        guests_list = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'flex-center')]"))
        )
        print("Guests modal and list loaded successfully!")
    except Exception as e:
        print(f"Error waiting for the guest list to load: {e}")
        driver.quit()
        return []

    # Wait for the page to load completely
    time.sleep(15)

    # Step 3: Scrape the guest names from the modal
    html = driver.page_source 

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find all guest containers (anchor <a> tags that contain the href attribute and names)
    guest_elements = soup.find_all('a', href=True)

    guest_inspection = []
    # Extract guest names and profile links
    if guest_elements:
        for guest in guest_elements:
            # Extract the profile link from the href attribute
            profile_link = guest['href']
            
            # Extract the guest name (inside nested <div> with the class 'name text-ellipses fw-medium')
            name_div = guest.find('div', class_="name text-ellipses fw-medium")
            if name_div:
                guest_name = name_div.text.strip()
                print(f"Guest: {guest_name}, Profile Link: {profile_link}")
                guest_inspection.append({"name": guest_name, "profile_link": profile_link})
    else:
        print("No guest elements found or incorrect class targeted!")

    # Close the browser after scraping
    driver.quit()

    # Return the list of guests with names and profile links
    return guest_inspection


def get_linkedin_from_guest_profile(profile_url):
    # Initialize Safari WebDriver (you can use any driver)
    driver = webdriver.Safari()

    # Open the guest profile page
    driver.get(profile_url)

    # Wait for the page to load completely
    #time.sleep(5)

    # Step 1: Wait for the social links section to load
    try:
        # Wait for the element with class 'social-links' to appear
        social_links = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "social-links"))
        )
        print("Social links section loaded successfully!")
    except Exception as e:
        print(f"Error waiting for the social links to load: {e}")
        driver.quit()
        return None

    # Step 2: Scrape the LinkedIn URL from the social links
    html = driver.page_source

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')


    
    # Find the social links section
    social_links = soup.find_all('div', class_="social-link")
    
    # Initialize variable to store LinkedIn URL
    linkedin_url = None
    
    # Iterate over social links and look for LinkedIn URL
    for link in social_links:
        a_tag = link.find('a', href=True)
        if a_tag and 'linkedin.com' in a_tag['href']:
            linkedin_url = a_tag['href']
            break
    
    # Return the LinkedIn URL if found
    if linkedin_url:
        return linkedin_url
    else:
        return "LinkedIn URL not found."
    
 
def extract_linkedin_profile(linkedin_url):
    try:
        url = "https://api.prospeo.io/linkedin-email-finder"

        required_headers = {
            'Content-Type': 'application/json',
            'X-KEY': KEY_LINKEDIN
        }
        
        data = {
            'url': linkedin_url
        }
        
        response = requests.post(url, json=data, headers=required_headers)
        return response.json()
    except Exception as e:
        print(f"Error fetching LinkedIn profile: {e}")
        return None
