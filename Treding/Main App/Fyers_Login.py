from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from pyotp import TOTP
from fyers_apiv3 import fyersModel

# Define global variables
userid = "YJ00129"
mobileno = "7069668308"
client_id = "MACO3YJA7I-100"
secret_key = "N7SXUFQG91"
redirect_uri = "https://trade.fyers.in/api-login/redirect-uri/index.html"
response_type = "code"
grant_type = "authorization_code"
state = "sample_state"
app_pin = "2525"
totp_key = "XKS2IVVGAINIHYVLM32WOXLFMQUK4DRA"

def get_access_token():
    global userid, mobileno, client_id, secret_key, redirect_uri, response_type, grant_type, state, app_pin, totp_key

    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key, 
        redirect_uri=redirect_uri, 
        response_type=response_type, 
        grant_type=grant_type
    )
    auth_link = session.generate_authcode()

    driver = webdriver.Chrome()
    try:
        driver.get(auth_link)
        driver.implicitly_wait(5)
        time.sleep(2)

        driver.find_element(By.ID, "mobile-code").send_keys(mobileno)
        driver.find_element(By.ID, "mobileNumberSubmit").click()
        time.sleep(4)
        myotp = TOTP(totp_key).now()
        driver.find_element(By.XPATH, '//*[@id="first"]').send_keys(myotp[0])
        driver.find_element(By.XPATH, '//*[@id="second"]').send_keys(myotp[1])
        driver.find_element(By.XPATH, '//*[@id="third"]').send_keys(myotp[2])
        driver.find_element(By.XPATH, '//*[@id="fourth"]').send_keys(myotp[3])
        driver.find_element(By.XPATH, '//*[@id="fifth"]').send_keys(myotp[4])
        driver.find_element(By.XPATH, '//*[@id="sixth"]').send_keys(myotp[5])
        driver.find_element(By.XPATH, '//*[@id="confirmOtpSubmit"]').click()
        time.sleep(2)
        driver.find_element(By.ID, 'pin-container').find_element(By.ID, 'first').send_keys(app_pin[0])
        driver.find_element(By.ID, 'pin-container').find_element(By.ID, 'second').send_keys(app_pin[1])
        driver.find_element(By.ID, 'pin-container').find_element(By.ID, 'third').send_keys(app_pin[2])
        driver.find_element(By.ID, 'pin-container').find_element(By.ID, 'fourth').send_keys(app_pin[3])
        driver.find_element(By.ID, 'verifyPinSubmit').click()
        time.sleep(2)
        current_url = driver.current_url
        auth_code = current_url[current_url.index('auth_code=')+10:current_url.index('&state')]

        session.set_token(auth_code)
        response = session.generate_token()
        access_token = response['access_token']
        
        with open('access_token.txt', 'w') as file:
            file.write(access_token)

        print("Access Token saved successfully.")
        # return access_token
        
    finally:
        driver.quit()

