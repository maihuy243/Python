from base.constants import WINDOW_WIDTH, WINDOW_HEIGHT, NUM_COLUMN, TOTAL_WINDOW
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time


def caculatePositionOfChrome():
    # Tính số hàng cần thiết
    num_rows = (TOTAL_WINDOW + NUM_COLUMN - 1) // NUM_COLUMN  
    positions = []
    for row in range(num_rows):
        for col in range(NUM_COLUMN):
            index = row * NUM_COLUMN + col
            if index < TOTAL_WINDOW:  # Chỉ thêm tọa độ nếu chưa đạt số lượng cửa sổ yêu cầu
                x = col * WINDOW_WIDTH
                y = row * WINDOW_HEIGHT
                positions.append((x,y))
    return positions


# Open chrome
def open_chrome_windows(args):
    drivers = []  # Danh sách để giữ các driver
    positions = caculatePositionOfChrome()

    for pos in positions:
        try:
            # Set Chrome options
            options = webdriver.ChromeOptions()
            options.add_argument(f"--window-position={pos[0]},{pos[1]}")
            options.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-notifications")
            options.add_argument("--mute-audio")
            driver = webdriver.Chrome(options=options)
            drivers.append(driver)

            # Custom action

        except WebDriverException as e:
            print(f"Error launching Chrome at position {pos}: {e}")
            continue  # Skip this position and move on to the next one

    # Giữ các cửa sổ mở trong 10 giây
    time.sleep(10)

    # Đóng tất cả các cửa sổ Chrome
    for driver in drivers:
        driver.quit()

# Import data txt
def read_file_lines(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        return lines 
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
        return []
    except IOError:
        print("An error occurred while reading the file.")
        return []

