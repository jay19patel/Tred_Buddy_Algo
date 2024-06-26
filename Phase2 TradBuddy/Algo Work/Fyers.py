from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from pyotp import TOTP
from fyers_apiv3 import fyersModel
import os
import pandas as pd
import pytz
from datetime import datetime , timedelta,date

class Fyers:
    def __init__(self) -> None:

        self.userid = "YJ00129"
        self.mobileno = "7069668308"
        self.client_id = "MACO3YJA7I-100"
        self.secret_key = "N7SXUFQG91"
        self.app_pin = "2525"
        self.totp_key = "XKS2IVVGAINIHYVLM32WOXLFMQUK4DRA"
        self.redirect_uri = "https://trade.fyers.in/api-login/redirect-uri/index.html"
        self.response_type = "code"
        self.grant_type = "authorization_code"
        self.state = "sample_state"
        self.authenticate = False
        self.access_token = None



    def get_access_token(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        session = fyersModel.SessionModel(
            client_id=self.client_id,
            secret_key=self.secret_key, 
            redirect_uri=self.redirect_uri, 
            response_type=self.response_type, 
            grant_type=self.grant_type
        )
        auth_link = session.generate_authcode()

        driver = webdriver.Chrome(options=chrome_options)
        try:
            driver.get(auth_link)
            time.sleep(2)

            driver.find_element(By.ID, "mobile-code").send_keys(self.mobileno)
            driver.find_element(By.ID, "mobileNumberSubmit").click()
            time.sleep(4)
            myotp = TOTP(self.totp_key).now()
            driver.find_element(By.XPATH, '//*[@id="first"]').send_keys(myotp[0])
            driver.find_element(By.XPATH, '//*[@id="second"]').send_keys(myotp[1])
            driver.find_element(By.XPATH, '//*[@id="third"]').send_keys(myotp[2])
            driver.find_element(By.XPATH, '//*[@id="fourth"]').send_keys(myotp[3])
            driver.find_element(By.XPATH, '//*[@id="fifth"]').send_keys(myotp[4])
            driver.find_element(By.XPATH, '//*[@id="sixth"]').send_keys(myotp[5])
            driver.find_element(By.XPATH, '//*[@id="confirmOtpSubmit"]').click()
            time.sleep(2)
            driver.find_element(By.ID, 'pin-container').find_element(By.ID, 'first').send_keys(self.app_pin[0])
            driver.find_element(By.ID, 'pin-container').find_element(By.ID, 'second').send_keys(self.app_pin[1])
            driver.find_element(By.ID, 'pin-container').find_element(By.ID, 'third').send_keys(self.app_pin[2])
            driver.find_element(By.ID, 'pin-container').find_element(By.ID, 'fourth').send_keys(self.app_pin[3])
            driver.find_element(By.ID, 'verifyPinSubmit').click()
            time.sleep(2)
            current_url = driver.current_url
            auth_code = current_url[current_url.index('auth_code=')+10:current_url.index('&state')]

            session.set_token(auth_code)
            response = session.generate_token()
            access_token = response['access_token']
            
            with open(f'{os.getcwd()}/Records/access_token.txt', 'w') as file:
                file.write(access_token)
            
        finally:
            print("[ Fyers Access Token  ]")
            driver.quit()

    def authentication(self):
        if not self.authenticate:
            access_token_path = f"{os.getcwd()}/Records/access_token.txt"
            if not os.path.exists(access_token_path):
                open(access_token_path, 'a').close()
            access_token = open(access_token_path, 'r').read().strip()
            if access_token:
                try:
                    fyers = fyersModel.FyersModel(client_id=self.client_id, is_async=False, token=access_token, log_path="")
                    print(f"Successful Login: {fyers.get_profile()['data']['name']}")
                    self.authenticate = True
                    self.access_token = access_token
                    self.fyers_instance = fyers
                    print("[ Fyers Authenticated  ]")
                
                except Exception as e:
                    print(f" Authentication Error:{e}")
                    print(" [ Resolve Error Again.... ]")
                    self.get_access_token()
                    self.authentication()
                    
            else:
                self.get_access_token()
                self.authentication()
                print("[ Resolve Error Again.... ]")

        else:
            print("[ Alredy Authenticated ]")

    def get_current_ltp(self, option_symbol):
            if self.authenticate:
                data = {"symbols": option_symbol}
                data = self.fyers_instance.quotes(data=data)
                if data['code'] == 200:
                    return {item['v'].get('short_name', 'Unknown'): item['v'].get('lp', 'Unknown') for item in data['d']}
                else:
                    print("[DATA NOT GET FROM FYERS]")
                    return False
            else:
                print("[ERROR: Authentication Failed]")
                return "[ERROR: Authentication Failed]"
    def MarketStatus(self):
        market_status = self.fyers_instance.market_status()
        return market_status["marketStatus"][0]["status"]
            
    def Historical_Data(self,Symbol,TimeFrame):
        data = {
                    "symbol":Symbol,
                    "resolution": TimeFrame,
                    "date_format":"1",
                    "range_from":(datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
                    "range_to":datetime.now().strftime('%Y-%m-%d'),
                    "cont_flag":"0"
                }
        row_data =  self.fyers_instance.history(data=data)
        if row_data['s']== "ok":
            df = pd.DataFrame.from_dict(row_data['candles'])
            columns_name = ['Datetime','Open','High','Low','Close','Volume']
            df.columns = columns_name
            df['Datetime'] = pd.to_datetime(df['Datetime'], unit='s')
            df['Datetime'] = df['Datetime'].dt.tz_localize(pytz.utc).dt.tz_convert('Asia/Kolkata')
            df['Datetime'] = df['Datetime'].dt.tz_localize(None)
            return df
        else:
            return row_data['s']



