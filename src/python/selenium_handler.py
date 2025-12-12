import os
import time

import selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

university_sso_logins = {'Michigan':'https://online.umich.edu/accounts/login?target=/'}

driver = None

#Username and password for SSO
def init(username, password, university) -> bool:
  global driver
  web = university_sso_logins[university]
  path = os.getenv('CHROMEDRIVER_PATH')
  op = selenium.webdriver.ChromeOptions()
  op.add_argument("user-data-dir=selenium")
  # op.add_argument('headless')
  service = Service(executable_path=path)
  driver = selenium.webdriver.Chrome(service=service, options=op)

  driver.get(web)

  driver.find_element(By.ID, 'username').send_keys(username)
  driver.find_element(By.ID, 'password').send_keys(password)

  driver.find_element(By.ID, 'loginSubmit').click()
  button_found = False
  if "duosecurity" not in driver.current_url:
    driver.quit()
    return False
  time.sleep(0.25)
  while True:
    test = "test"
    try:
      if "duosecurity" in driver.current_url:
        driver.find_element(By.ID, 'trust-browser-button')
        button_found = True
      break
    except:
      time.sleep(1)
  if button_found:
    driver.find_element(By.ID, 'trust-browser-button').click()
  return True

  driver.get('https://instruct.math.lsa.umich.edu/webwork2/ma116-024-f24')
  # driver.find_element(By.ID, 'username').send_keys(username)
  # driver.find_element(By.ID, 'password').send_keys(password)
  #
  # driver.find_element(By.ID, 'loginSubmit').click()
  #
  # while True:
  #   try:
  #     driver.find_element(By.ID, 'trust-browser-button')
  #     break
  #   except:
  #     time.sleep(1)
  #
  # driver.find_element(By.ID, 'trust-browser-button').click()

def get_webwork_assignments(classID, section):
  driver.get('https://instruct.math.lsa.umich.edu/webwork2/'+ classID +'-'+ section +'-f24')
  achieve_assignments = driver.find_elements(By.XPATH, '//li[@class="list-group-item d-flex align-items-center justify-content-between"and@data-set-status="open"]')
  return achieve_assignments;
