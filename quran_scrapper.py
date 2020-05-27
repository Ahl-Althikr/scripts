"""
AUTHOR: Abdelrahman Salem
DATE: May 26, 2020
------------------------------------------------
USE CASE STATEMENT
------------------------------------------------
This script is used to scrap `web.mushafmakkah.com` for quranic verse data that include information about:
    - surah:
        - surah name in english and arabic unicode representation
        - surah number
        - surah basmala
        - surah verses
    - ayah:
        - ayah arabic unicode representation
        - ayah words in arabic unicode representation
        - ayah page number
        - ayah juzi number
        - ayah number in english and arabic unicode representation

The data is used to generate three JSON data structures:
    1. JSON by surah: where data is grouped by surah number
    2. JSON by page: where data is grouped by page number
    3. JSON by juzi: : where data is grouped by juzi number
"""
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re
import time
import json
import copy
import argparse

# ------------------------------------------------
# Command Line Arguments
# ------------------------------------------------
parser = argparse.ArgumentParser(description='Scrap the Mushafmakkah Quran Web App')
parser.add_argument('-hd', '--headless', help='Run scrapping with headless browser', action='store_true')
parser.add_argument('-l', '--log', help='Log scrapping data in realtime', action='store_true')
parser.add_argument('-lwd', '--log-width', help='Log width size', type=int, default=20)
parser.add_argument('-qw', '--query-wait', help='Set query wait time out', type=float, default=10)
parser.add_argument('-sw', '--script-wait', help='Set script wait time out', type=float, default=10)
parser.add_argument('-lw', '--load-wait', help='Set load wait time out', type=float, default=10)
parser.add_argument('-f', '--file-prefix', help='Set file name prefix', default='data/quran_')
parser.add_argument('-i', '--indent', help='Set output indentation', type=int, default=2)

args = parser.parse_args()

# ------------------------------------------------
# Constants
# ------------------------------------------------
URL = 'https://web.mushafmakkah.com/#!/?sura=1&aya=1&lang=ar'
FILE_NAME = args.file_prefix + '{0}.json'
TEXT_ATTR = 'innerText'
NO_BASMALA = (1, 9)

# ------------------------------------------------
# Config
# ------------------------------------------------
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--incognito')
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('--disable-notifications')
chrome_options.add_argument('--disable-extensions')

if args.headless:
    chrome_options.add_argument('--headless')

chrome_options.experimental_options['prefs'] = {
    'profile.managed_default_content_settings.images': 2,
    'profile.default_content_setting_values.notifications': 2,
    'profile.managed_default_content_settings.stylesheets': 2,
    'profile.managed_default_content_settings.javascript': 1,
    'profile.managed_default_content_settings.plugins': 1,
    'profile.managed_default_content_settings.popups': 2,
    'profile.managed_default_content_settings.geolocation': 2,
    'profile.managed_default_content_settings.media_stream': 2,
}

driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(args.load_wait)
driver.set_script_timeout(args.script_wait)
driver.rewrite_rules = [
    (r'(https?://).*(mp3|reciters|ttf|woff2|woff|png|gif|svg|jpg).*', 'http://127.0.0.1')
]

wait = WebDriverWait(driver, args.query_wait)

# ------------------------------------------------
# Utils
# ------------------------------------------------

def log(key, value, wrapper=None):
    if args.log:
        if wrapper is not None: print(wrapper * args.log_width)
        print(key + ': ' + str(value))
        if wrapper is not None: print(wrapper * args.log_width)

def click_element(element):
    try:
        element.click()
    except:
        driver.execute_script('arguments[0].click();', element)

# ------------------------------------------------
# Selectors
# ------------------------------------------------
TAFSIR_TAB = "div.HeaderInner nav > a.headerTabLink:nth-child(2)"

PAGE_LIST = '#soura-tab > div.soura-list > ul > li.hidden'
PAGE_NUMBER = 'div.item-after > span.badge'
PAGE_CONTENT = 'div#page_{0}'
PAGE_CLICK = 'div.item-content'
PAGE_WAIT = 'div#page_{0} span.aya'

VERSE_LIST = 'div#page_{0} span.aya'
VERSE_CHAPTER = 'span.SuraTitleWrap'
VERSE_BASMALA = 'img.bismalah'
VERSE_ARABIC_UNICODE_LIST = 'span.page_{0}'
VERSE_EXPLANATION_NAME = 'span.TafseerText span.tafsir-title'
VERSE_EXPLANATION_TEXT = 'span.TafseerText span.TafseerText'
VERSE_CLICK = 'span'
VERSE_WAIT = 'div#page_{0} span.aya.ayaActive:nth-child({1})'

ACTIVE_SECTION = '#main_home_title > a'

ACTIVE_CHAPTER = '.soura-list-itemChecked'
ACTIVE_CHAPTER_NAME = '.item-after > span:first-child'
ACTIVE_CHAPTER_NUMBER = '.item-after > span.badge'
ACTIVE_CHAPTER_ARABIC_UNICODE = '.item-title'

# ------------------------------------------------
# Element Getters
# ------------------------------------------------
def get_tafsir_tab_element():
    return driver.find_element_by_css_selector(TAFSIR_TAB)


def get_page_list_elements():
    return driver.find_elements_by_css_selector(PAGE_LIST)

def get_page_number_element(page_element):
    return page_element.find_element_by_css_selector(PAGE_NUMBER)

def get_page_content_element(page_number):
    return driver.find_element_by_css_selector(PAGE_CONTENT.format(page_number))


def get_verse_list_elements(page_number):
    return driver.find_elements_by_css_selector(VERSE_LIST.format(page_number))

def get_verse_chapter_element(verse_element):
    return verse_element.find_element_by_css_selector(VERSE_CHAPTER)

def get_verse_basmala_element(verse_element):
    return verse_element.find_element_by_css_selector(VERSE_BASMALA)

def get_verse_arabic_unicode_elements(verse_element, page_number):
    return verse_element.find_elements_by_css_selector(VERSE_ARABIC_UNICODE_LIST.format(page_number))

def get_verse_explanation_name_element(verse_element):
    return verse_element.find_element_by_css_selector(VERSE_EXPLANATION_NAME)

def get_verse_explanation_text_element(verse_element):
    return verse_element.find_element_by_css_selector(VERSE_EXPLANATION_TEXT)


def get_active_section_element():
    return driver.find_element_by_css_selector(ACTIVE_SECTION)


def get_active_chapter_element():
    return driver.find_element_by_css_selector(ACTIVE_CHAPTER)

def get_active_chapter_name_element(active_chapter_element):
    return active_chapter_element.find_element_by_css_selector(ACTIVE_CHAPTER_NAME)

def get_active_chapter_number_element(active_chapter_element):
    return active_chapter_element.find_element_by_css_selector(ACTIVE_CHAPTER_NUMBER)

def get_active_chapter_arabic_unicode_element(active_chapter_element):
    return active_chapter_element.find_element_by_css_selector(ACTIVE_CHAPTER_ARABIC_UNICODE)

# ------------------------------------------------
# Value Getters
# ------------------------------------------------
def get_page_number(page_element):
    return int(get_page_number_element(page_element).get_attribute(TEXT_ATTR))


def get_verse_arabic_unicode(verse_arabic_unicode_element):
    return verse_arabic_unicode_element.get_attribute(TEXT_ATTR)


def get_verse_number(verse_element, page_number):
    return int(re.sub(r'sura_[0-9]+_aya_', '', verse_element.find_element_by_css_selector(VERSE_ARABIC_UNICODE_LIST.format(page_number)).get_attribute('id')))

def get_verse_explanation_text(verse_element):
    return get_verse_explanation_text_element(verse_element).get_attribute(TEXT_ATTR)

def get_verse_explanation_name(verse_element):
    return get_verse_explanation_name_element(verse_element).get_attribute(TEXT_ATTR)


def get_section_number():
    return int(re.sub(r'[^0-9]', '', get_active_section_element().get_attribute(TEXT_ATTR)))


def get_chapter_number(active_chapter_element):
    return int(get_active_chapter_number_element(active_chapter_element).get_attribute(TEXT_ATTR))

def get_chapter_name(active_chapter_element):
    return get_active_chapter_name_element(active_chapter_element).get_attribute(TEXT_ATTR)

def get_chapter_arabic_unicode(active_chapter_element):
    return re.sub(r'[0-9]+', '', get_active_chapter_arabic_unicode_element(active_chapter_element).get_attribute(TEXT_ATTR))


# ------------------------------------------------
# Fetch
# ------------------------------------------------
driver.get(URL)

# ------------------------------------------------
# Data
# ------------------------------------------------

verses = {}
pages = {}
chapters = {}
sections = {}
explanations = {}

languages = {
    'AR': {
        'id': 'AR',
        'name': 'Arabic',
    },
    'EN': {
        'id': 'EN',
        'name': 'English',
    },
}

# ------------------------------------------------
# Scrapping
# ------------------------------------------------

if __name__ != '__main__':
    exit()
try:
    current_chapter = 0
    current_section = 0

    click_element(get_tafsir_tab_element())

    for page_element in get_page_list_elements():
        click_element(page_element.find_element_by_css_selector(PAGE_CLICK))

        page_number = get_page_number(page_element)
        page_id = page_number
        pages[page_id] = {
            'id': page_id,
            'number': page_number,

            'verses': [],
            'chapters': set([]),
            'sections': set([]),
        }
        
        log('Page', page_id, '=')
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PAGE_WAIT.format(page_number))))

        for verse_index, verse_element in enumerate(get_verse_list_elements(page_number), 1):
            click_element(verse_element.find_element_by_css_selector(VERSE_CLICK))
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, VERSE_WAIT.format(page_number, verse_index))))

            active_chapter = get_active_chapter_element()

            verse_number = get_verse_number(verse_element, page_number)
            chapter_number = get_chapter_number(active_chapter)
            section_number = get_section_number()

            verse_id = str(chapter_number) + ':' + str(verse_number)
            explanation_id = verse_id
            chapter_id = chapter_number
            section_id = section_number

            explanations[explanation_id] = {
                'id': explanation_id,
                'text': get_verse_explanation_text(verse_element),
                'name': get_verse_explanation_name(verse_element),
                'language': 'AR',

                'verse': verse_id,
                'page': page_id,
                'section': section_id,
                'chapter': chapter_id,
            }

            verses[verse_id] = {
                'id': verse_id,
                'number': verse_number,
                'arabic_unicodes': [get_verse_arabic_unicode(ar_unicode_el) for ar_unicode_el in get_verse_arabic_unicode_elements(verse_element, page_number)],

                'explanations': [explanation_id],
                'page': page_id,
                'section': section_id,
                'chapter': chapter_id,
            }

            if chapter_id != current_chapter:
                current_chapter = chapter_id
                chapters[chapter_id] = {
                    'id': chapter_id,
                    'number': chapter_number,
                    'name': get_chapter_name(active_chapter),
                    'aranic_unicode': get_chapter_arabic_unicode(active_chapter),
                    'basmalah': chapter_id not in NO_BASMALA,
                    
                    'verses': [],
                    'pages': [],
                    'sections': set([]),
                }

                log('Chapter', chapter_id, "-")
            if section_id != current_section:
                current_section = section_id
                sections[section_id] = {
                    'id': section_id,
                    
                    'verses': [],
                    'pages': [],
                    'chapters': set([]),
                }

                log('Section', section_id, "*")

            chapters[chapter_id]['sections'].add(section_id)
            pages[page_id]['sections'].add(section_id)
            
            sections[section_id]['chapters'].add(chapter_id)
            pages[page_id]['chapters'].add(chapter_id)    

            chapters[chapter_id]['verses'].append(verse_id)
            sections[section_id]['verses'].append(verse_id)
            pages[page_id]['verses'].append(verse_id)

            log('Verse', verse_id)
        
        chapters[current_chapter]['pages'].append(page_id)
        sections[current_section]['pages'].append(page_id)
except (KeyboardInterrupt, SystemExit):
    pass
finally:
    with open(FILE_NAME.format('languages'), 'w') as languages_file:
        json.dump(languages, languages_file, indent=args.indent)
    with open(FILE_NAME.format('verses'), 'w') as verses_file:
        json.dump(verses, verses_file, indent=args.indent)
    with open(FILE_NAME.format('pages'), 'w') as pages_file:
        json.dump(pages, pages_file, indent=args.indent)
    with open(FILE_NAME.format('chapters'), 'w') as chapters_file:
        json.dump(chapters, chapters_file, indent=args.indent)
    with open(FILE_NAME.format('sections'), 'w') as sections_file:
        json.dump(sections, sections_file, indent=args.indent)
    with open(FILE_NAME.format('explanations'), 'w') as explanations_file:
        json.dump(explanations, explanations_file, indent=args.indent)
        
    driver.quit()