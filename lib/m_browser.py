from selenium import webdriver


def browser_start(headless):
    useragent = "Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36"

    options = webdriver.FirefoxOptions()
    options.set_preference("general.useragent.override", useragent)
    options.set_preference("dom.webnotifications.serviceworker.enabled", False)
    options.set_preference("dom.webnotifications.enabled", False)

    if headless == True:
        options.add_argument("--headless")

    browser = webdriver.Firefox(options=options)
    return browser


def browser_cookie_save(cookies):
    with open("db/cookies/user.txt", "w") as f:
        for cookie in cookies:
            cookie_fields = [
                "name",
                "value",
                "domain",
                "path",
                "expiry",
                "secure",
                "httpOnly",
            ]
            tmpcokkie = ""

            for cookie_field in cookie_fields:
                try:
                    tmpcokkie += f"{cookie[cookie_field]}\t"
                except:
                    tmpcokkie += f"0\t"

            f.write(tmpcokkie[:-1] + "\n")

    return True


def browser_cookie_load(browser):
    print("Existing cookie found: Setting Cookie...")

    with open("db/cookies/user.txt", "r") as f:
        for line in f:
            line = line.strip().split("\t")

            cookie = {
                "name": line[0],
                "value": line[1],
                "domain": line[2],
                "path": line[3],
                "expiry": int(line[4]),
                "secure": line[5] == "True",
                "httpOnly": line[6] == "True",
            }
            browser.add_cookie(cookie)
