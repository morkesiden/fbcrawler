import sqlite3
from lib.m_browser import browser_start
from lib.m_fbfunctions import fb_signin, post_reactions
from lib.m_tools import remove_temps
from lib.m_sql import sql_init,obtener_db_fbids
import time

browser = browser_start(False)
signed_in = fb_signin(browser)

db_fbids = obtener_db_fbids()


if signed_in:
    for post_profile, post_id in db_fbids:
        print("crawling ... fbid:" + post_id)
        post_reactions(browser, post_profile, post_id)
        time.sleep(1)

    browser.quit()
    # remove_temps()
    print("finish")
