def clockin():
    print("Clock In Script Triggered!")
    import os
    from dotenv import load_dotenv
    import selenium
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import NoSuchElementException
    import time
    load_dotenv()
    
    username = os.getenv("user")
    password = os.getenv("pass")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    driver.get('https://mlytics.webhr.co/hr/login/')

    username_field = driver.find_element(By.ID, 'u')
    password_field = driver.find_element(By.ID, 'p')
    username_field.send_keys(username)
    password_field.send_keys(password)
    time.sleep(10)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "btnLogin"))).click()
    time.sleep(10)
    try:   
        try:
            driver.find_element(By.ID, 'btnAttendanceSignIn')
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "btnAttendanceSignIn"))).click()
            from app import reply_clockedin
            reply_clockedin()
        except NoSuchElementException:
            try:
                driver.find_element(By.ID, 'btnAttendanceSignBackIn')
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "btnAttendanceSignBackIn"))).click()
                from app import reply_clockedin
                reply_clockedin()
            except NoSuchElementException:
                from app import reply_error
                reply_error()
    except selenium.common.exceptions.TimeoutException:
        from app import reply_error
        reply_error()
    driver.close()