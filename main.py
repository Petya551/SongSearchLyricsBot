import telebot
from bs4 import BeautifulSoup
import requests
import os
from selenium import webdriver   # for webdriver
from telebot import types
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait  # for implicit and explict waits
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

song_bot = telebot.TeleBot("2128007635:AAHuDH8KQlA_RwNDSHE_v2ME2I4tHizdWV8")
replaced_singer = ""

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en,uk-UA;q=0.9,uk;q=0.8,en-US;q=0.7",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Mobile Safari/537.36",
    "From": "petrohavryluk6@gmail.com"
}

counter_song = 0
song_links = None
page_url = None

def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def choose_song_action(message):
    global page_url
    global counter_song
    if message.text == "Next":
        counter_song += 1
        driver.get(f"{page_url}")
        driver.get(driver.find_element_by_xpath(f"/html/body/table[2]/tbody/tr/td[1]/div/table[2]/tbody/tr[{counter_song+2}]/td[1]/a").get_attribute("href"))
        song_text = driver.find_element_by_class_name("songwords").text

        menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        menu.add(types.KeyboardButton("Previous"),
                 types.KeyboardButton("Next"),
                 types.KeyboardButton("Search By Words"),
                 types.KeyboardButton("Author + Song Name"))
        user_choice = song_bot.send_message(message.chat.id, f"{song_text}", reply_markup=menu)
        song_bot.register_next_step_handler(user_choice, choose_song_action)

    elif message.text == "Previous":
        if counter_song > 0:
            counter_song -= 1
            driver.get(f"{page_url}")
            driver.get(driver.find_element_by_xpath(f"/html/body/table[2]/tbody/tr/td[1]/div/table[2]/tbody/tr[{counter_song + 2}]/td[1]/a").get_attribute("href"))
            song_text = driver.find_element_by_class_name("songwords").text

            menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            menu.add(types.KeyboardButton("Previous"),
                     types.KeyboardButton("Next"),
                     types.KeyboardButton("Search By Words"),
                     types.KeyboardButton("Author + Song Name"))
            user_choice = song_bot.send_message(message.chat.id, f"{song_text}", reply_markup=menu)
            song_bot.register_next_step_handler(user_choice, choose_song_action)
        else:
            song_bot.send_message(message.chat.id, "There is no previous song")

    elif message.text == "Song Words":
        counter_song = 0
        words = song_bot.send_message(message.chat.id, "Type words:")
        song_bot.register_next_step_handler(words, get_song_words)

    elif message.text == "Author + Song Name":
        counter_song = 0
        user_song = song_bot.send_message(message.chat.id, "Type:")
        song_bot.register_next_step_handler(user_song, get_song_name_aurthor)

def get_song_words(message):
    global counter_song
    global page_url
    mssg = message.text
    song_bot.send_message(message.chat.id, "Wait a minute...")

    driver.get("https://www.pisni.org.ua/")

    input_box = driver.find_element_by_xpath("/html/body/div[1]/table/tbody/tr/td[10]/input[1]")
    input_box.send_keys(f"{mssg}")

    input_button = driver.find_element_by_xpath("/html/body/div[1]/table/tbody/tr/td[10]/a[1]")
    input_button.click()

    page_url = driver.current_url

    driver.get(driver.find_element_by_xpath(f"/html/body/table[2]/tbody/tr/td[1]/div/table[2]/tbody/tr[{counter_song+2}]/td[1]/a").get_attribute("href"))
    song_text = driver.find_element_by_class_name("songwords").text

    if song_text:
        menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        menu.add(types.KeyboardButton("Previous"),
                       types.KeyboardButton("Next"),
                        types.KeyboardButton("Song Words"),
                 types.KeyboardButton("Author + Song Name"))
        user_choice = song_bot.send_message(message.chat.id, f"{song_text}", reply_markup=menu)
        song_bot.register_next_step_handler(user_choice, choose_song_action)
    else:
        mssg = song_bot.send_message(message.chat.id, "Bot can't find lyrics for the song")
        song_bot.register_next_step_handler(mssg, tell_something)

# def get_song_pisni_ua(message):
#     mssg = message.text
#     song_bot.send_message(message.chat.id, "Wait a minute...")
#
#     driver.get("https://pisni.ua/")
#
#     input_box = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div/ul/li[2]/form/div[2]/input")
#     input_box.send_keys(f"{mssg}")
#
#     input_button = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div/ul/li[2]/form/div[1]/input")
#     input_button.click()
#     driver.execute_script("arguments[0].click()", input_button)
#
#     song_bot.send_message(message.chat.id, "1")
#
#     # page_url = driver.current_url
#     # if driver.find_element_by_xpath(f"/html/body/div[3]/div[1]/div[2]/div/div[2]/div/div[1]/div/a").is_displayed():
#     if check_exists_by_xpath("/html/body/div[3]/div[1]/div[2]/div/div[2]/div/div[1]/div/a"):
#
#         search_link = driver.find_element_by_xpath(f"/html/body/div[3]/div[1]/div[2]/div/div[2]/div/div[1]/div/a").get_attribute("href")
#         song_bot.send_message(message.chat.id, f"{search_link}")
#         song_bot.send_message(message.chat.id, "1")
#
#         driver.get(search_link)
#         song_text = driver.find_element_by_xpath("/html/body/div[3]/div[1]/div[2]/div/div[2]/div[1]/div[2]/div/div").text
#         song_bot.send_message(message.chat.id, "1")
#
#         menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#         menu.add(types.KeyboardButton("Song Words"),
#                  types.KeyboardButton("Author + Song Name"))
#         user_choice = song_bot.send_message(message.chat.id, f"{song_text}", reply_markup=menu)
#         song_bot.register_next_step_handler(user_choice, choose_song_action)
#     else:
#         mssg = song_bot.send_message(message.chat.id, "Bot can't find lyrics for the song (Pisni)")
#         # song_bot.register_next_step_handler(mssg, tell_something)
#         song_bot.register_next_step_handler(mssg, get_song_genius)

# def get_song_genius(message):
#     mssg = message.text
#     song_bot.send_message(message.chat.id, "Wait a minute...")
#
#     driver.get("https://genius.com/")
#
#     input_box = driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/form/input")
#     input_box.send_keys(f"{mssg}")
#
#     # input_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/form/div/")
#     input_button = driver.find_element_by_xpath("//div[contains(@class, 'global_search-submit_button u-clickable')]")
#     input_button.click()
#     song_bot.send_message(message.chat.id, "1")
#
#     # page_url = driver.current_url
#     if driver.find_element_by_xpath(f"/html/body/routable-page/ng-outlet/search-results-page/div/div[2]/div[1]/div[1]/search-result-section/div/div[2]/search-result-items/div/search-result-item/div/mini-song-card/a").is_displayed():
#         search_link = driver.find_element_by_xpath(f"/html/body/routable-page/ng-outlet/search-results-page/div/div[2]/div[1]/div[1]/search-result-section/div/div[2]/search-result-items/div/search-result-item/div/mini-song-card/a").get_attribute("href")
#         driver.get(search_link)
#         song_text = driver.find_element_by_xpath("/html/body/routable-page/ng-outlet/song-page/div/div/div[2]/div[1]/div/defer-compile[1]/lyrics/div/div/section/p").text
#
#         menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#         menu.add(types.KeyboardButton("Song Words"),
#                  types.KeyboardButton("Author + Song Name"))
#         user_choice = song_bot.send_message(message.chat.id, f"{song_text}", reply_markup=menu)
#         song_bot.register_next_step_handler(user_choice, choose_song_action)
#     else:
#         mssg = song_bot.send_message(message.chat.id, "Bot can't find lyrics for the song (Genius)")
#         song_bot.register_next_step_handler(mssg, get_song_letras)

def get_song_name_aurthor(message):
    #-----------------------------------------------LETRAS----------------------------------------------------------------
    mssg = message.text
    song_bot.send_message(message.chat.id, "Wait a minute...")

    driver.get(f"https://mp3uk.net/")
    song_bot.send_message(message.chat.id, "0")

    input_box = driver.find_element(By.XPATH, f"/html/body/div[1]/div/div/div/div/header/div[3]/form/div/input")
    input_box.send_keys(f"{mssg}")
    song_bot.send_message(message.chat.id, "1")
    input_button = driver.find_element_by_xpath(f"/html/body/div[2]/div/div/div/div/header/div[3]/form/div/button")
    input_button.click()
    song_bot.send_message(message.chat.id, "2")

    # page_url = driver.current_url
    temp_counter = 2
    if check_exists_by_xpath(f"/html/body/div[2]/div/div/div/div/main/div[2]/div[{temp_counter}]"): # /html/body/div[2]/div/div/div/div/main/div[2]/div[3]
        div_dict = {}
        title_list = driver.find_elements_by_class_name("track-title").text
        subtitle_list = driver.find_elements_by_class_name("track-subtitle").text

        # k = 0
        # for i in div_list:
            # title = driver.find_elements_by_xpath(f"/html/body/div[2]/div/div/div/div/main/div[2]/div[{temp_counter+k}]/a[1]/div[1]").text #/html/body/div[2]/div/div/div/div/main/div[2]/div[3]/a[1]/div[1]
            # author = driver.find_elements_by_xpath(f"/html/body/div[2]/div/div/div/div/main/div[2]/div[{temp_counter+k}]/a[1]/div[2]").text #/html/body/div[2]/div/div/div/div/main/div[2]/div[3]/a[1]/div[1]
            # div_dict[title] = author
            # k += 1
        temp_string = ""
        k = 1
        for i, j in title_list, subtitle_list:
            temp_string += f"{k}. {i} -- {j}\n"

        song_bot.send_message(message.chat.id, temp_string)
        #
        # search_link = driver.find_element_by_xpath(f"/html/body/div[1]/div[1]/div[1]/div[2]/div/div/div/div/div/div/div/div[5]/div[2]/div/div/div[1]/div[1]/div[1]/div[1]/div/a").get_attribute("href")
        # song_bot.send_message(message.chat.id, "3")
        #
        # driver.get(search_link)
        # song_bot.send_message(message.chat.id, "4")
        # song_text = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div[6]/article/div[2]/div[2]").text
        # song_bot.send_message(message.chat.id, "5")
        #
        # menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        # menu.add(types.KeyboardButton("Song Words"),
        #          types.KeyboardButton("Author + Song Name"))
        # user_choice = song_bot.send_message(message.chat.id, f"{song_text}", reply_markup=menu)
        # song_bot.register_next_step_handler(user_choice, choose_song_action)


    else:
        #----------------------------------------GL5-----------------------------------------------------------------
        mssg = song_bot.send_message(message.chat.id, "Bot can't find lyrics for the song")
        song_bot.register_next_step_handler(mssg, choose_song_action)

    #     mssg = message.text
    #     song_bot.send_message(message.chat.id, "Wait a minute...")
    #
    #     driver.get("https://www.gl5.ru/")
    #
    #     delay = 3  # seconds
    #     try:
    #         input_box = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/header/div/div[2]/div/div/div/div/form/table/tbody/tr/td[1]/div/table/tbody/tr/td[1]/input')))
    #         song_bot.send_message(message.chat.id, "The page is done")
    #     except TimeoutException:
    #         song_bot.send_message(message.chat.id, "Something went wrong")
    #
    #     # input_box = driver.find_element_by_xpath("/html/body/header/div/div[2]/div/div/div/div/form/table/tbody/tr/td[1]/div/table/tbody/tr/td[1]/input")
    #     input_box.send_keys(f"{mssg}")
    #     song_bot.send_message(message.chat.id, "1")
    #     input_button = driver.find_element_by_xpath("/html/body/header/div/div[2]/div/div/div/div/form/table/tbody/tr/td[2]/button")
    #     input_button.click()
    #     song_bot.send_message(message.chat.id, "2")
    #
    #     # page_url = driver.current_url
    #     if check_exists_by_xpath(f"/html/body/header/div/div[2]/div/div/div/div/div/div[5]/div[2]/div/div/div[1]/div[1]/div[1]/div[1]/div/a"):
    #         search_link = driver.find_element_by_xpath(f"/html/body/header/div/div[2]/div/div/div/div/div/div[5]/div[2]/div/div/div[1]/div[1]/div[1]/div[1]/div/a").get_attribute("href")
    #         song_bot.send_message(message.chat.id, "3")
    #
    #         driver.get(search_link)
    #         song_bot.send_message(message.chat.id, "4")
    #         song_text = driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div[1]/div/div[4]").text
    #         song_bot.send_message(message.chat.id, "5")
    #
    #         menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    #         menu.add(types.KeyboardButton("Song Words"),
    #                  types.KeyboardButton("Author + Song Name"))
    #         user_choice = song_bot.send_message(message.chat.id, f"{song_text}", reply_markup=menu)
    #         song_bot.register_next_step_handler(user_choice, choose_song_action)
    #     else:
    #         song_bot.send_message(message.chat.id, "Bot can't find lyrics for the song (Gl5)")
    #         #-------------------------------------LYRICSHUB----------------------------------------------------------------------
    #         mssg = message.text
    #         song_bot.send_message(message.chat.id, "Wait a minute...")
    #
    #         driver.get("https://lyricshub.ru/")
    #
    #         delay = 3  # seconds
    #         try:
    #             input_box = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,'/html/body/div[2]/div/div[2]/form/input')))
    #             song_bot.send_message(message.chat.id, "The page is done")
    #         except TimeoutException:
    #             song_bot.send_message(message.chat.id, "Something went wrong")
    #         # input_box = driver.find_element_by_xpath("/html/body/div[2]/div/div[2]/form/input")
    #         input_box.send_keys(f"{mssg}")
    #         song_bot.send_message(message.chat.id, "1")
    #         input_button = driver.find_element_by_xpath("/html/body/div[2]/div/div[2]/form/button")
    #         input_button.click()
    #         song_bot.send_message(message.chat.id, "2")
    #
    #         # page_url = driver.current_url
    #         if check_exists_by_xpath("/html/body/div[2]/div/div[1]/div/div[1]/div[2]/div[2]/a"):
    #             search_link = driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div/div[1]/div[2]/div[2]/a").get_attribute("href")
    #             song_bot.send_message(message.chat.id, "3")
    #
    #             driver.get(search_link)
    #             song_bot.send_message(message.chat.id, "4")
    #             song_text = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[2]/div/div[1]/div[4]").text
    #             song_bot.send_message(message.chat.id, "5")
    #
    #             menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    #             menu.add(types.KeyboardButton("Song Words"),
    #                      types.KeyboardButton("Author + Song Name"))
    #             user_choice = song_bot.send_message(message.chat.id, f"{song_text}", reply_markup=menu)
    #             song_bot.register_next_step_handler(user_choice, choose_song_action)
    #         else:
    #             mssg = song_bot.send_message(message.chat.id, "Bot can't find lyrics for the song (LyricsHub)")
    #             # -------------------------------------PISNI_UA----------------------------------------------------------------------
    #             mssg = message.text
    #             song_bot.send_message(message.chat.id, "Wait a minute...")
    #
    #             driver.get("https://pisni.ua/")
    #
    #             delay = 3  # seconds
    #             try:
    #                 input_box = WebDriverWait(driver, delay).until(
    #                     EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div/ul/li[2]/form/div[2]/input')))
    #                 song_bot.send_message(message.chat.id, "The page is done")
    #             except TimeoutException:
    #                 song_bot.send_message(message.chat.id, "Something went wrong")
    #             # input_box = driver.find_element_by_xpath("/html/body/div[2]/div/div[2]/form/input")
    #             input_box.send_keys(f"{mssg}")
    #             song_bot.send_message(message.chat.id, "1")
    #             input_button = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div/ul/li[2]/form/div[1]/input")
    #             input_button.click()
    #             song_bot.send_message(message.chat.id, "2")
    #
    #             # page_url = driver.current_url
    #             if check_exists_by_xpath("/html/body/div[3]/div[1]/div[2]/div/div[2]/div/div[1]/div/a"):
    #                 search_link = driver.find_element_by_xpath("/html/body/div[3]/div[1]/div[2]/div/div[2]/div/div[1]/div/a").get_attribute("href")
    #                 song_bot.send_message(message.chat.id, "3")
    #
    #                 driver.get(search_link)
    #                 song_bot.send_message(message.chat.id, "4")
    #                 song_text = driver.find_element_by_xpath("/html/body/div[3]/div[1]/div[2]/div/div[2]/div[1]/div[2]/div").text
    #                 song_bot.send_message(message.chat.id, "5")
    #
    #                 menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    #                 menu.add(types.KeyboardButton("Song Words"),
    #                          types.KeyboardButton("Author + Song Name"))
    #                 user_choice = song_bot.send_message(message.chat.id, f"{song_text}", reply_markup=menu)
    #                 song_bot.register_next_step_handler(user_choice, choose_song_action)
    #             else:
    #                 mssg = song_bot.send_message(message.chat.id, "Bot can't find lyrics for the song (LyricsHub)")
    #                 song_bot.register_next_step_handler(mssg, tell_something)
#
# def get_song_gl(message):
#     mssg = message.text
#     song_bot.send_message(message.chat.id, "Wait a minute...")
#
#     driver.get("https://www.gl5.ru/")
#
#     input_box = driver.find_element_by_xpath("/html/body/header/div/div[2]/div/div/div/div/form/table/tbody/tr/td[1]/div/table/tbody/tr/td[1]/input")
#     input_box.send_keys(f"{mssg}")
#     song_bot.send_message(message.chat.id, "1")
#     input_button = driver.find_element_by_xpath("/html/body/header/div/div[2]/div/div/div/div/form/table/tbody/tr/td[2]/button")
#     input_button.click()
#     song_bot.send_message(message.chat.id, "2")
#
#     # page_url = driver.current_url
#     if check_exists_by_xpath(f"/html/body/header/div/div[2]/div/div/div/div/div/div[5]/div[2]/div/div/div[1]/div[1]/div[1]/div[1]/div/a"):
#         search_link = driver.find_element_by_xpath(f"/html/body/header/div/div[2]/div/div/div/div/div/div[5]/div[2]/div/div/div[1]/div[1]/div[1]/div[1]/div/a").get_attribute("href")
#         song_bot.send_message(message.chat.id, "3")
#
#         driver.get(search_link)
#         song_bot.send_message(message.chat.id, "4")
#         song_text = driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div[1]/div/div[4]").text
#         song_bot.send_message(message.chat.id, "5")
#
#         menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#         menu.add(types.KeyboardButton("Song Words"),
#                  types.KeyboardButton("Author + Song Name"))
#         user_choice = song_bot.send_message(message.chat.id, f"{song_text}", reply_markup=menu)
#         song_bot.register_next_step_handler(user_choice, choose_song_action)
#     else:
#         mssg = song_bot.send_message(message.chat.id, "Bot can't find lyrics for the song (Gl5)")
#         song_bot.register_next_step_handler(mssg, get_song_gl)

@song_bot.message_handler(content_types=["text"])
def tell_something(message):
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu.add(types.KeyboardButton("Song Words"),
             types.KeyboardButton("Author + Song Name"))
    user_choice = song_bot.send_message(message.chat.id, "Choose action", reply_markup=menu)
    song_bot.register_next_step_handler(user_choice, choose_song_action)


song_bot.infinity_polling()