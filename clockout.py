def clockout():
    print("Clock Out Script Trigger!")
    import os
    from dotenv import load_dotenv
    import selenium
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time
    load_dotenv()
    
    username = os.getenv("user")
    password = os.getenv("pass")

    chrome_driver_path = ChromeDriverManager().install()
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    driver.get('https://mlytics.webhr.co/hr/login/')

    username_field = driver.find_element(By.ID, 'u')
    password_field = driver.find_element(By.ID, 'p')
    username_field.send_keys(username)
    password_field.send_keys(password)
    time.sleep(5)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "btnLogin"))).click()
    time.sleep(5)
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "btnAttendanceSignOut"))).click()
        from app import reply_signedout
        reply_signedout()
    except selenium.common.exceptions.TimeoutException:
        from app import reply_already_signedout
        reply_already_signedout()
    driver.close()