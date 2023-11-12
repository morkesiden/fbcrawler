import json
import os
import re
from selenium.webdriver.common.by import By

import datetime
import pytz


def get_profiles():
    db_profiles = []
    with open("db/urls_profiles.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            db_profiles.append(line.strip())
    return db_profiles


def see_more_button_present(xbrowser):
    try:
        xbrowser.find_element(By.XPATH, "//span[contains(text(),'See more stories')]")
        return True
    except:
        return False


def convertir_fecha_desde_timestamp(timestamp):
    fecha_legible = datetime.datetime.fromtimestamp(timestamp)
    timezone = pytz.timezone("America/Tijuana")

    fecha_legible_timezone = fecha_legible.replace(tzinfo=pytz.utc).astimezone(timezone)
    fecha_formateada = fecha_legible_timezone - datetime.timedelta(hours=-7)
    # fecha_formateada = fecha_formateada.strftime('%Y-%m-%d %H:%M:%S %Z%z') #          24 Hrs
    fecha_formateada = fecha_formateada.strftime(
        "%Y-%m-%d %I:%M:%S %p %Z%z"
    )  #      12 Hrs

    return fecha_formateada


def extract_data_from_html(html_content):

    reactions_match = re.search(r'(?<=aria-label=")(\d+)(?= reactions)', html_content)
    reactions_count = reactions_match.group(1) if reactions_match else "0"

    comments_match = re.search(r"\b(\d+) Comments\b", html_content)
    comments_count = comments_match.group(1) if comments_match else "0"

    post_date = (
        re.search(r"publish_time&quot;:(\d{10})", html_content).group(1)
        if re.search(r"publish_time&quot;:\d{10}", html_content)
        else "N/A"
    )

    if 'N/A' not in post_date:
        post_date = convertir_fecha_desde_timestamp(int(post_date))
        
    post_id_match = re.search(
        r'story_fbid=([^&]+)', html_content
    )

    if post_id_match:
        post_id = post_id_match.group(1)
        #print(post_id)
    else:
        post_id = False


    return post_id, post_date, reactions_count, comments_count


db_reactions = []

with open("db/db_reactions.json") as f:
    data = json.load(f)

for react_id in data["reactions"]:
    react_type = data["reactions"][react_id]["type"]
    react_name = data["reactions"][react_id]["display_name"]

    db_reactions.append([react_type, react_name])


def extract_profile_id(profile):
    if "profile.php?id=" in profile:
        return profile.split("profile.php?id=")[-1]
    else:
        return profile.split("/")[-1]


def reaction2name(num):
    for react in db_reactions:
        if num == react[0]:
            return react[1]


def tocsv(post_id, profiles):
    with open(f"db/posts/db.csv", "a+") as a:
        with open(f"db/posts/post_{post_id}.csv", "w") as f:
            f.write("fb_id,reaction_id,profile_name,profile_url\n")

            for profile in profiles:
                record = (
                    str(post_id)
                    + ","
                    + str(profile["reaction_type"])
                    + ","
                    + profile["profile_name"]
                    + ","
                    + profile["profile_url"]
                    + "\n"
                )

                f.write(record)
                a.write(record)


def post_save_json(post_id, data):
    with open(f"db/posts/post_{post_id}.json", "w") as f:
        f.write(json.dumps(data, indent=4))


def remove_temps():
    os.remove("../geckodriver.log")
