import time
import threading
from selenium import webdriver
from base.index_base import caculatePositionOfChrome, read_file_lines
from base.constants import WINDOW_WIDTH,WINDOW_HEIGHT,PATH_FILE_VIA,TOTAL_WINDOW,TIME_WAIT_ELEMENT
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


active_drivers = 0
active_drivers_lock = threading.Lock()

def startLogingFb():
    global active_drivers
    positions = caculatePositionOfChrome()
    accounts = read_file_lines(PATH_FILE_VIA)
    for i, value in enumerate(accounts):

        with active_drivers_lock:
                while active_drivers >= TOTAL_WINDOW:
                    active_drivers_lock.release()
                    time.sleep(0.5)  
                    active_drivers_lock.acquire()

        with active_drivers_lock:
            active_drivers += 1

        position = positions[i % len(positions)]
        time.sleep(1)
        threading.Thread(target=process, args=(value, position,)).start()

  
def process(acc,position):
    global active_drivers
    try:
        # Set Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument(f"--window-position={position[0]},{position[1]}")
        options.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--mute-audio")
        driver = webdriver.Chrome(options=options)
        splitAcc = acc.split("|")
        username, password, twoFa, *_ = splitAcc
        driver.get("https://www.facebook.com/")

        inputUsername = WebDriverWait(driver,TIME_WAIT_ELEMENT).until(EC.presence_of_element_located(By.XPATH,""))



        time.sleep(1000)
        driver.quit()

    except TimeoutException:
        print("Element did not appear within the given time")
    except WebDriverException as e:
        print(f"Error launching Chrome: {e}")
    finally:
        with active_drivers_lock:
            active_drivers -= 1


   
