import time
import threading
from selenium import webdriver
from base.index_base import caculatePositionOfChrome, read_file_lines
from base.constants import WINDOW_WIDTH,WINDOW_HEIGHT,PATH_FILE_VIA,CHROME_DRIVER,TIME_WAIT_ELEMENT,PATH_FILE_LOG,TOTAL_WINDOW,PATH_IMG_CAPCHA
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from datetime import datetime

active_drivers = 0
active_drivers_lock = threading.Lock()

isAuthenticationUrl = "two_step_verification/authentication"
isTwoFactorUrl = "two_step_verification/two_factor"


def startLogingFb():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%d/%m/%Y %H:%M:%S")
    with open(PATH_FILE_LOG, "a") as file:
        file.write(f"---------------[ {formatted_time} ]---------------\n")
    global active_drivers
    positions = caculatePositionOfChrome()
    accounts = read_file_lines(PATH_FILE_VIA)
    for i, acc in enumerate(accounts):

        with active_drivers_lock:
                while active_drivers >= TOTAL_WINDOW:
                    active_drivers_lock.release()
                    time.sleep(0.5)  
                    active_drivers_lock.acquire()

        with active_drivers_lock:
            active_drivers += 1

        position = positions[i % len(positions)]
        threading.Thread(target=process, args=(acc, position,)).start()
        time.sleep(1)

  
def process(acc,position):
    global active_drivers
        # Set Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument(f"--window-position={position[0]},{position[1]}")
    options.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--mute-audio")
    options.add_argument("--headless")

    service = Service(CHROME_DRIVER)
    driver = webdriver.Chrome(service=service, options=options)
    try:
        splitAcc = acc.split("|")
        username, password, twoFa, *_ = [item.strip() for item in splitAcc]
        print(f"[ {username} ]: Bắt đầu check !")
        driver.get("https://www.facebook.com/")

        inputUsername = WebDriverWait(driver,TIME_WAIT_ELEMENT).until(EC.presence_of_element_located((By.XPATH,'//input[@id="email"]')))
        inputPassword = WebDriverWait(driver,TIME_WAIT_ELEMENT).until(EC.presence_of_element_located((By.XPATH,'//input[@id="pass"]')))
        buttonLogin = WebDriverWait(driver,TIME_WAIT_ELEMENT).until(EC.element_to_be_clickable((By.XPATH,'//button[@type="submit"]')))
        driver.implicitly_wait(2)

        inputUsername.send_keys(username)
        inputPassword.send_keys(password)
        driver.implicitly_wait(2)
        buttonLogin.click()
        currentUrl = driver.current_url
        if(currentUrl.__contains__(isAuthenticationUrl)):
            infoAcc = f"{username} | {password} | {twoFa} | Capcha".replace("\n", " ")
            print(f"[ {username} ]: Spam ip - Capcha !")
            with open(PATH_FILE_LOG, "a") as file:
                    file.write(f"{infoAcc}\n")
            time.sleep(3)
            driver.quit()

        if(currentUrl.__contains__(isTwoFactorUrl)):
            print(f"[ {username} ]: Bắt đầu lấy code 2Fa !")
            driver.execute_script("window.open('https://gauth.apps.gbraad.nl');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get("https://gauth.apps.gbraad.nl")
            buttonAdd2Fa = WebDriverWait(driver,TIME_WAIT_ELEMENT).until(EC.element_to_be_clickable((By.XPATH,'//a[@id="addButton"]')))
            buttonAdd2Fa.click()
            driver.implicitly_wait(5)
            time.sleep(2)
            WebDriverWait(driver,TIME_WAIT_ELEMENT).until(EC.presence_of_element_located((By.XPATH,'//input[@id="keyAccount"]'))).send_keys(username)
            WebDriverWait(driver,TIME_WAIT_ELEMENT).until(EC.presence_of_element_located((By.XPATH,'//input[@id="keySecret"]'))).send_keys(twoFa)
            WebDriverWait(driver,TIME_WAIT_ELEMENT).until(EC.element_to_be_clickable((By.XPATH,'//a[@id="addKeyButton"]'))).click()
            driver.implicitly_wait(5)
            time.sleep(2)
            twoFaCode = WebDriverWait(driver, TIME_WAIT_ELEMENT).until(
                EC.visibility_of_element_located((By.XPATH, f'//span[text()="{username}"]//h3'))
            ).text

            all_tabs = driver.window_handles
            driver.switch_to.window(all_tabs[0])
            time.sleep(2)
            # Bind code 2Fa
            WebDriverWait(driver,TIME_WAIT_ELEMENT).until(EC.presence_of_element_located((By.XPATH,'//input[@type="text"]'))).send_keys(twoFaCode)

            try:
                form = driver.find_element(By.TAG_NAME, "form")
                form.submit()
            except NoSuchElementException:
                print("Cant find form submit")

            try:
                homeIcon = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'//a[@href="/"]')))
                homeIcon.click()
                driver.get("https://adsmanager.facebook.com/adsmanager/manage")
                buttonCreateAds = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'//div[@id="pe_toolbar"]//div[@role="toolbar"]/div[1]//span//div[@role="none"][1]/div')))
                isEnable = buttonCreateAds.get_attribute("disabled") is None or buttonCreateAds.get_attribute("aria-disabled") != "true" or "disabled" not in  buttonCreateAds.get_attribute("class")

                if isEnable:
                    with open(PATH_FILE_LOG, "a") as file:
                        file.write(f"{username} | {password} | {twoFa} | Live Ads\n")
                else:
                    print(f"[ {username} ]: Die Ads !")

            except NoSuchElementException:
                print("Cant click home button !")   
          
        time.sleep(2)
        driver.quit()

    except TimeoutException:
        print("Element did not appear within the given time")
    except WebDriverException as e:
        print(f"Error launching Chrome: {e}")
    finally:
        with active_drivers_lock:
            active_drivers -= 1
        driver.quit()
        


   

