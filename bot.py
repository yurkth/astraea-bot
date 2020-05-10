from io import BytesIO
from base64 import b64decode
from os import environ

import tweepy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from wand.image import Image


def get_planet_data():
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(environ["CHROME_DRIVER_PATH"], options=options)
        driver.get(environ["ASTRAEA_URL"])
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return frameCount > 1")
        )
        name = driver.execute_script("return rng.seed")
        b64 = driver.execute_script("return canvas.toDataURL()")
    finally:
        driver.quit()

    with Image(blob=b64decode(b64.replace("data:image/png;base64,", ""))) as img:
        img.crop(width=192, height=108, gravity="center")
        img.sample(*map(lambda x: x * 3, img.size))
        resized = BytesIO(img.make_blob())

    return {"name": name, "image": resized}


def tweet(message, file):
    consumer_key = environ["CONSUMER_KEY"]
    consumer_secret = environ["CONSUMER_SECRET"]
    access_token = environ["ACCESS_TOKEN"]
    access_secret = environ["ACCESS_SECRET"]
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
    api.update_with_media(status=message, filename="planet.png", file=file)


if __name__ == "__main__":
    planet = get_planet_data()
    tweet(planet["name"], planet["image"])
