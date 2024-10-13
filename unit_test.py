import csv
from methods.agent_scrapper import scrape_guests_from_event, get_linkedin_from_guest_profile, extract_linkedin_profile
from methods.agent_openai import get_profile

linkedin_url="https://www.linkedin.com/in/adonai-vera/"
# TEST (unit_test.py)
#"https://www.linkedin.com/in/alexander-lum-havrilla/"
#"https://www.linkedin.com/in/zhuohan-l/"
#"https://www.linkedin.com/in/adonai-vera/"

profile_info = extract_linkedin_profile(linkedin_url)  # Profile of LinkedIn

print(profile_info)
# Get profile summary using OpenAI (or another agent)
agent_response = get_profile(profile_info)  # Extract profile summary from the API

print(agent_response)