#!/usr/bin/python3
"""
Check Rivian Shop for a matching config
"""
# Changelog
# 0.2.0 - February 8, 2024
#   Rivian changed their shop to a new URL and a few other things, updated to work with the new shop
# 0.1.0 - September 2, 2023
#   Initial coding
from __future__ import print_function
import argparse
import logging
import os
import subprocess
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin


# Set up colors for logging
logging.addLevelName(logging.CRITICAL, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.CRITICAL))
logging.addLevelName(logging.ERROR,    "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING,  "\033[1;34m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName(logging.INFO,     "\033[1;35m%s\033[1;0m" % logging.getLevelName(logging.INFO))
logging.addLevelName(logging.DEBUG,    "\033[1;33m%s\033[1;0m" % logging.getLevelName(logging.DEBUG))


def check_inventory_via_clicking(args, driver):
    """Select Filters"""
    driver.get("https://rivian.com/configurations/list")
    # Lazy sleep for page to load the zip code dialog
    time.sleep(10)
    # Close the cookie thing
    find_cookie = driver.find_elements(By.CSS_SELECTOR,"[class^='onetrust-close-btn-handler banner-close-button ot-close-icon']")
    find_cookie[0].click()
    time.sleep(2)
    zipcode_box = driver.find_element(By.CSS_SELECTOR,"[name='deliveryZipCode']")
    zipcode_box.send_keys(args.zip)
    zipcode_box.send_keys(Keys.RETURN)
    # Lazy sleep to wait for filters to load
    time.sleep(30)
    # Check the toggle to switch to R1S (if you want a R1T delete/comment this)
    find_toggle = driver.find_elements(By.CSS_SELECTOR,"[class^='toggleInput absolute left-0 z-[1] m-0 h-full w-full cursor-pointer select-none p-0 opacity-0']")
    find_toggle[0].click()
    time.sleep(2)
    # Check if there are vehicles listed
    check_filtered_results = driver.find_elements(By.CSS_SELECTOR,"[class^='swiper']")
    if len(check_filtered_results) == 0:
        logging.warning("No results, exiting.")
        if args.debug is True:
            time.sleep(10)
        driver.quit()
        exit(0)
    # Click the colors we want to look for
    driver.find_element(By.XPATH, "//button[contains(@class, 'relative mr-auto box-border') and contains(., 'Red Canyon')]").click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[contains(@class, 'relative mr-auto box-border') and contains(., 'Compass Yellow')]").click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[contains(@class, 'relative mr-auto box-border') and contains(., 'Rivian Blue')]").click()
    time.sleep(2)
    # Collapse the paint section
    paint_collapse = driver.find_element(By.XPATH, "//div[contains(@class, 'MuiButtonBase-root MuiAccordionSummary-root') and contains(., 'Paint')]")
    paint_collapse.click()
    # Scroll down to allow us to click more options
    scroll_origin = ScrollOrigin.from_element(paint_collapse)
    ActionChains(driver).scroll_from_origin(scroll_origin, 0, 200).perform()
    time.sleep(2)
    # Click the motors we want to look for  
    driver.find_element(By.XPATH, "//button[contains(@class, 'relative mr-auto box-border') and contains(., 'Performance Dual-Motor AWD')]").click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[contains(@class, 'relative mr-auto box-border') and contains(., 'Quad-Motor AWD')]").click()
    time.sleep(2)
    # Collapse the drive system section
    driver.find_element(By.XPATH, "//div[contains(@class, 'MuiButtonBase-root MuiAccordionSummary-root') and contains(., 'Drive system')]").click()
    time.sleep(2)
    # Click the batteries we want to look for  
    driver.find_element(By.XPATH, "//button[contains(@class, 'relative mr-auto box-border') and contains(., 'Up to 400 mi')]").click()
    time.sleep(2)
    # Collapse the batteries section
    driver.find_element(By.XPATH, "//div[contains(@class, 'MuiButtonBase-root MuiAccordionSummary-root') and contains(., 'Battery')]").click()
    time.sleep(2)
    # Click the tires we want to look for  
    driver.find_element(By.XPATH, "//button[contains(@class, 'relative mr-auto box-border') and contains(., 'Road')]").click()
    time.sleep(2)
    # Collapse the tires section
    wheels_collapse = driver.find_element(By.XPATH, "//div[contains(@class, 'MuiButtonBase-root MuiAccordionSummary-root') and contains(., 'Wheels and tires')]")
    wheels_collapse.click()
    # Scroll down to allow us to click more options
    scroll_origin = ScrollOrigin.from_element(wheels_collapse)
    ActionChains(driver).scroll_from_origin(scroll_origin, 0, 200).perform()
    time.sleep(2)
    # Click the interiors we want to look for  
    driver.find_element(By.XPATH, "//button[contains(@class, 'relative mr-auto box-border') and contains(., 'Ocean Coast') and contains(., 'Dark Ash Wood')]").click()
    time.sleep(2)
    # Click the "show reuslts" button
    driver.find_element(By.XPATH, "//button[contains(@class, 'MuiButtonBase-root MuiButton-root MuiButton-contained') and contains(., 'Show Results')]").click()
    time.sleep(30)
    # Check if there are vehicles listed
    check_filtered_results = driver.find_elements(By.CSS_SELECTOR,"[class^='swiper']")
    if len(check_filtered_results) == 0:
        logging.warning("No results, exiting.")
        if args.debug is True:
            time.sleep(10)
        driver.quit()
        exit(0)
    # If we make it here then we found results, hooray!
    driver.save_screenshot('/tmp/selenium_screenshot.png')
    logging.info("Found a match, alerting via email!")
    return



def start_selenium():
    """Start our browser driver."""
    driver = webdriver.Chrome()
    driver.get("https://rivian.com/account")
    driver.maximize_window()
    driver.implicitly_wait(2)
    return driver


def login_to_rivian(driver, args):
    """Take the selenium driver and log into Rivian"""
    username_box = driver.find_element(By.CSS_SELECTOR,"[aria-label='Email']")
    username_box.send_keys(args.username)
    password_box = driver.find_element(By.CSS_SELECTOR,"[aria-label='Password']")
    password_box.send_keys(args.password)
    submit_button = driver.find_element(By.CSS_SELECTOR,"[data-testid='Signin-button-submit']")
    if args.debug is True:
        # Allow a human to watch/check inputs
        time.sleep(5)
    submit_button.click()
    # Lazy sleep to wait for page to load
    time.sleep(10)
    return


def check_if_at_login(driver, args):
    """Verify we are on the login page"""
    test_results = None
    try:
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"[aria-label='Email']")))
        if args.debug is True:
            logging.debug("Found the sign in box, we are at the login page.")
        return True
    except Exception:  # This shoudl be a better error like TimeoutException
        logging.debug("did not find the sign in box, we are not at the login page.")
        return False


def email_notification(args, url):
    """Send an email using OS mailx since it is already configured for us"""
    email_body_file = open('/tmp/mailx_body.txt', "w")
    email_body_file.write(url)
    email_body_file.close()
    time.sleep(2) # wait for FS flags to clear, 2 seconds is an eternity but whatever
    subprocess.Popen('mailx -A /tmp/selenium_screenshot.png -s "Rivian Shop Has Inventory" ' + args.email + ' < /tmp/mailx_body.txt', shell=True)
    time.sleep(5) # Need to give the subprocess tiem to read the files otherwise they are gone before it can read them
    os.remove('/tmp/mailx_body.txt')
    os.remove('/tmp/selenium_screenshot.png')
    logging.info("Email sent, exiting.")
    return


def main():
    """The true main function."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='\033[1;33mCheck Rivian Shop for a matching config, use %2C to list multiple choices. Example "--battery BAT-B01%2CBAT-A01" .\033[1;0m'
        )
    parser.add_argument('--username',  dest='username', default=None, required=True, help='Your Rivian.com username.')
    parser.add_argument('--password',  dest='password', default=None, required=True, help='Your Rivian.com password.')
    parser.add_argument('--email',     dest='email',    default=None, required=True, help='Your notification email account.')
    parser.add_argument('--zip',       dest='zip',      default=None, required=True, help='Your zip code.')
    parser.add_argument('--debug',     dest='debug',    action='store_true')
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format="[%(levelname)8s] %(message)s")
    else:
        logging.basicConfig(level=logging.INFO,  format="[%(levelname)8s] %(message)s")
    driver = start_selenium()
    if check_if_at_login(driver, args):
        login_to_rivian(driver, args)
    if check_if_at_login(driver, args):
        logging.error("Still at login page, quitting.")
        driver.quit()
        exit(0)
    check_inventory_via_clicking(args, driver)
    email_notification(args, "https://rivian.com/configurations/list")
    return


if __name__ == '__main__':
    main()
    exit()
