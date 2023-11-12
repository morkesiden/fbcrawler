import os
import time
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from lib.m_browser import browser_cookie_load, browser_cookie_save
from lib.m_tools import reaction2name, post_save_json, tocsv
from lib.m_sql import add_reactions

fb_reactions_url = (
    "https://mbasic.facebook.com/ufi/reaction/profile/browser/?ft_ent_identifier="
)


def fb_signin(browser):
    fb_user = "julio_ibarr@hotmail.com"
    fb_pass = "asdasd123"
    fb_start_page = "https://m.facebook.com/"

    print("Logging in %s automatically..." % 'fb_user')

    browser.get(fb_start_page)

    if os.path.exists("db/cookies/user.txt"):
        browser_cookie_load(browser)
        return True

    browser.get(fb_start_page)

    email_id = browser.find_element(By.ID, "m_login_email")
    pass_id = browser.find_element(By.ID, "m_login_password")
    confirm_id = browser.find_element(By.NAME, "login")
    email_id.send_keys(fb_user)
    pass_id.send_keys(fb_pass)
    confirm_id.click()
    time.sleep(3)

    # 2FA
    if "checkpoint" in browser.current_url:
        otp_id = browser.find_element(By.ID, "approvals_code")
        continue_id = browser.find_element(By.ID, "checkpointSubmitButton")

        fb_otp = input("Enter OTP: ")
        otp_id.send_keys(fb_otp)
        continue_id.click()

    time.sleep(3)

    browser_cookie_save(browser.get_cookies())


def parse_count(count_str):
    if "K" in count_str:
        # Remove 'K' and convert to float, then multiply by 1000
        return int(float(count_str.replace("K", "")) * 1000)
    else:
        # Convert other formats directly to integers
        return int(count_str)


def post_reactions(browser ,post_profile, post_id):
    browser.get(f"{fb_reactions_url}{post_id}")

    post_elements = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[role="button"]'))
    )
    
    urls = []
    data = {}

    data["post_id"] = post_id
    data["reactions_counts"] = []


    try:
        reaction = {
            "name": "All",
            "id": 0,
            "count": int(post_elements[0].text.split(" ")[1]),
        }

        data["reactions_counts"].append(reaction)
    except:
        pass

    skipped_first = False

    for post_element in post_elements:

        if not skipped_first: 
            skipped_first = True
            continue 

        post_text = post_element.text
  
        url = post_element.get_attribute("href").replace("limit=10", "limit=50")
        urls.append(url)

        parse_url = urlparse(url)
        parse_params = parse_qs(parse_url.query)
        reaction_id = parse_params["reaction_type"][0]
        reaction_name = reaction2name(int(reaction_id))

        print('crawling - ',reaction_name)
        
        count = parse_count(post_text)

        reaction = {
            "name": reaction_name,
            "id": int(reaction_id),
            "count": int(count),
        }
        
        #print (reaction)
        data["reactions_counts"].append(reaction)

    reaction_profiles_all = []
    next_url = ""

    data["reactions"] = []

    for url in urls:
        time.sleep(1)
        next_url = ""
        parse_url = urlparse(url)
        parse_params = parse_qs(parse_url.query)

        reaction_id = int(parse_params["reaction_type"][0])
        reaction_total = int(parse_params["total_count"][0])
        reaction_name = reaction2name(reaction_id)

        reaction = {
            "name": reaction_name,
            "id": reaction_id,
            "count": reaction_total,
            "profiles": [],
        }

        while next_url != "none":
            next_url = ""

            browser.get(url)

            try:
                temp_profiles = WebDriverWait(browser, 5).until(
                    lambda x: x.find_elements(By.CLASS_NAME, "be")
                )

                reaction_profiles, next_url = get_reaction_profiles(
                    temp_profiles, reaction_id
                )

                reaction_profiles_all.extend(reaction_profiles)
                reaction["profiles"] = reaction_profiles
            except:
                next_url = "none"

            if next_url != "none":
                url = next_url

        data["reactions"].append(reaction)

    add_reactions(post_profile, post_id, reaction_profiles_all)
    #tocsv(post_id, reaction_profiles_all)
    #post_save_json(post_id, data)


def get_reaction_profiles(profiles_list, reaction_type):
    reaction_profiles = []
    more_url = "none"

    for profile in profiles_list:
        try:
            elem = profile.find_element(By.CLASS_NAME, "bj")
            profile_url = "https://facebook.com" + str(
                elem.get_attribute("innerHTML").split('"')[1::2][0]
            )
            profile_url = profile_url.split("?eav=", 1)[0].split("&amp;eav=", 1)[0]
            data = {
                "profile_name": profile.text,
                "profile_url": profile_url,
                "reaction_type": reaction_type,
            }
            reaction_profiles.append(data)

        except NoSuchElementException:
            try:
                elem = profile.find_element(By.CLASS_NAME, "f")
                more_url = "https://mbasic.facebook.com" + str(
                    elem.get_attribute("innerHTML")
                    .replace("limit=10", "limit=50")
                    .replace("&amp;", "&")
                    .split('"')[1::2][0]
                )
            except:
                print(f"Failed to retrieve profile details for {profile.text}")

    return reaction_profiles, more_url
