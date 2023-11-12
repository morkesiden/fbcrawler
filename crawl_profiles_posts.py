import time
from lib.m_browser import browser_start
from lib.m_fbfunctions import fb_signin
from lib.m_sql import sql_init, add_post_to_db
from lib.m_tools import (
    extract_profile_id,
    see_more_button_present,
    get_profiles,
    extract_data_from_html,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def profile_postids(profile, post_count, browser):
    print("Crawling Profile:" + profile)
    profile_url = profile + "?v=timeline"
    browser.get(profile_url)

    total_posts_collected = 0

    print('\n\n')
    print(
        "                      ",
        "profile",
        "\t\t",
        "date",
        "\t\t\t",
        "reactions",
        "\t",
        "comments",
    )

    while total_posts_collected < post_count and see_more_button_present(browser):

        posts_elements = WebDriverWait(browser, 10).until(
            lambda x: x.find_elements(By.XPATH, "//div[@role='article']")
        )

        
        for post in posts_elements:
            html_content = post.get_attribute("outerHTML")
            profile_id = extract_profile_id(profile)

            (
                post_id,
                post_date,
                count_reactions,
                count_comments,
            ) = extract_data_from_html(html_content)

            if post_id == False: continue

            add_post_to_db(
                profile_id, post_id, post_date, count_reactions, count_comments
            )
            total_posts_collected += 1
            print("un total de :", total_posts_collected)

        if total_posts_collected < post_count:
            see_more_button = browser.find_element(
                By.XPATH, "//span[contains(text(),'See more stories')]"
            )
            see_more_button.click()
            time.sleep(2)

    print("All task completed")


if __name__ == "__main__":
    sql_init()
    browser = browser_start(False)
    signed_in = fb_signin(browser)

    db_profiles = get_profiles()

    if signed_in:
        for profile in db_profiles:
            profile_postids(profile, 500, browser)

    browser.quit()
    print("Browser quitted.")
