import time
from random import choice, shuffle
import os

from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image


def compare_images(image_one, image_two):
    img1 = Image.open(image_one)
    img2 = Image.open(image_two)
    if list(img1.getdata()) == list(img2.getdata()):
        return True
    return False


def get_random_useragent():
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]

    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent


def get_web_driver():
    options = Options()
    options.headless = False
    options.add_argument("--log-level=3")
    options.add_experimental_option(
        "excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    prefs = {"intl.accept_languages": 'en_US,en',
             "credentials_enable_service": False,
             "profile.password_manager_enabled": False,
             "profile.default_content_setting_values.notifications": 2,
             "download_restrictions": 3}
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option('extensionLoadTimeout', 120000)
    options.add_argument(f"user-agent={get_random_useragent()}")
    options.add_argument("--mute-audio")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-features=UserAgentClientHint')
    options.add_argument("--disable-web-security")
    webdriver.DesiredCapabilities.CHROME['loggingPrefs'] = {
        'driver': 'OFF', 'server': 'OFF', 'browser': 'OFF'}

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(0.75)
    return driver


def click_popup(driver, element):
    driver.execute_script(
        "arguments[0].scrollIntoViewIfNeeded();", element)
    time.sleep(1)
    element.click()


def bypass_popup(driver):
    url = driver.current_url.split("?")[0]
    if url == "https://www.youtube.com/supported_browsers":
        driver.find_element(By.ID, "return-to-youtube").click()

    try:
        agree = WebDriverWait(driver, 5).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '#text')))
        click_popup(driver=driver, element=agree)
    except WebDriverException:
        try:
            agree = driver.find_element(
                By.XPATH,
                f'//*[@aria-label="{choice(["Accept", "Reject"])} the use of cookies and other data for the purposes described"]')
            click_popup(driver=driver, element=agree)
        except WebDriverException:
            pass


def bypass_other_popup(driver):
    popups = ['Got it', 'Skip trial', 'No thanks', 'Dismiss', 'Not now']
    shuffle(popups)

    for popup in popups:
        try:
            driver.find_element(
                By.XPATH, f"//*[@id='button' and @aria-label='{popup}']").click()
        except WebDriverException:
            pass


def change_playback_speed(driver):
    driver.find_element(By.ID, 'movie_player').send_keys(">>>>")


def get_video_duration(driver):
    try:
        full_duration_element = driver.find_element(By.CLASS_NAME, "ytp-time-duration")
        full_minutes, full_seconds = full_duration_element.text.split(":")
        full_duration = (int(full_minutes) * 60) + int(full_seconds)
        watched_duration = driver.find_element(By.CLASS_NAME, "ytp-time-current")
        watched_minutes, watched_seconds = watched_duration.text.split(":")
        watched_duration = (int(watched_minutes) * 60) + int(watched_seconds)
        duration_remaining = full_duration - watched_duration
        return duration_remaining
    except:
        time.sleep(10)
        get_video_duration(driver)


def skip_again(driver):
    try:
        skip_ad = driver.find_element(
            By.CLASS_NAME, "ytp-ad-skip-button-container")
        driver.execute_script("arguments[0].click();", skip_ad)
    except WebDriverException:
        pass


def play_video(driver):
    element = driver.find_element(By.CSS_SELECTOR,
                                  "#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-left-controls > button")
    aria_label = element.get_attribute("aria-label")

    try:
        driver.find_element(By.CLASS_NAME, 'ytp-play-button').click()
    except WebDriverException:
        try:
            driver.find_element(
                By.CLASS_NAME, 'html5-main-video').click()
        except WebDriverException:
            try:
                driver.find_element(
                    By.CSS_SELECTOR, '[title^="Play (k)"]').click()
            except WebDriverException:
                try:
                    driver.execute_script(
                        "document.querySelector('button.ytp-play-button.ytp-button').click()")
                except WebDriverException:
                    pass

    skip_again(driver)


def wait_initial_page_to_load(driver, url: str):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'content')))


def is_playing(driver):
    # hover to element for visibility
    a = ActionChains(driver)
    element = driver.find_element(By.CLASS_NAME, "ytp-play-button")
    a.move_to_element(element).perform()
    # get screenshot
    video_playing_element = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "ytp-play-button")))
    video_playing_element.screenshot("./src/screenshots/play_button.png")

    # convert image with black background
    img = Image.open("./src/screenshots/play_button.png")
    img = img.convert("RGBA")

    datas = img.getdata()

    newData = []

    for item in datas:
        if item[0] != 255 and item[1] != 255 and item[2] != 255:
            newData.append((0, 0, 0, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    img.save("./src/screenshots/play_button_with_background.png", "PNG")
    os.remove("./src/screenshots/play_button.png")

    # compare image
    val = compare_images("./src/screenshots/play_button_with_background.png", "./src/screenshots/video_is_playing.png")
    os.remove("./src/screenshots/play_button_with_background.png")
    return val


def error(driver, msg):
    driver.close()
    driver.quit()
    return msg


def main(url):
    if "www.youtube.com/watch?" not in url:
        raise ValueError("is not a youtube video!")
    driver = get_web_driver()
    driver.get(url)
    bypass_popup(driver)
    bypass_other_popup(driver)
    try:
        wait_initial_page_to_load(driver, url)
    except:
        return error(driver, "page not load")
    if "channel" in driver.current_url:
        return error(driver, "not found video")
    # stop autoplay
    driver.find_element(By.CSS_SELECTOR,
                        "#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-right-controls > button:nth-child(1)").click()
    if not is_playing(driver):
        play_video(driver)
    change_playback_speed(driver)
    video_duration = get_video_duration(driver)
    calc_tempo = (round(video_duration / 2)) + 5
    print(f"tempo rimanente: {calc_tempo}")
    time.sleep(calc_tempo)
    driver.close()
    driver.quit()
