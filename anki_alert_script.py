from datetime import datetime as dt
import os 

from bs4 import BeautifulSoup as bs
from requests import Session,post
import yaml

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE = "{}/history.log".format(DIR_PATH)
PARAMS_FILE = "{}/config_params.yaml".format(DIR_PATH)


###
def create_timestamp() -> str:
  now = dt.now()
  unix_timestamp = int(now.timestamp())
  date_string = now.strftime("%Y%m%d")
  time_string = now.strftime("%H:%M:%S")
  return  "{},{},{}".format(unix_timestamp,date_string,time_string)


###
def log_error(error_msg: str) -> None:
  log_string = "{},{}\n".format(create_timestamp(),error_msg)
  with open(LOG_FILE,'a') as file:
    file.write(log_string)
  raise SystemExit


###
def log_success(reviews_due: int) -> None:
  with open(LOG_FILE,'a') as file:
    file.write("{},Review status checked successfully ({})\n".format(create_timestamp(),reviews_due))


### Pull in user specific data from parameter file
def load_config_params(file_name: str) -> dict:
  try:
    with open(file_name) as file:
      params = yaml.load(file, Loader=yaml.FullLoader)
  except IOError:
    log_error("Issue opening or reading from parameters file")

  return params


### Login to ankiweb and grab the ankiweb.net/decks page
def scrape_ankiweb(params: dict) -> bytes:
  ANKI_LOGIN_FORM_POST_URL = 'https://ankiweb.net/account/login'
  ANKI_DECKS_URL = 'https://ankiweb.net/decks/'
  
  
  anki_login_payload = {
    'username': params['anki_username'],
    'password': params['anki_password'],
    'submitted':'1',
    'csrf_token': ''
  }
  
  with Session() as s:
    try:
      login_page = s.get(ANKI_LOGIN_FORM_POST_URL)
      bs_login_page = bs(login_page.content, 'html.parser')
    except: 
      log_error("Issue accessing anki login page")

    try:
      token = bs_login_page.find('input',{'name':'csrf_token'})['value']
      anki_login_payload['csrf_token']=token
    except (KeyError, TypeError):
      log_error("Unabled to find csrf token")
      
    post_response = s.post(ANKI_LOGIN_FORM_POST_URL, data=anki_login_payload)
    decks_page = s.get(ANKI_DECKS_URL)
    if (decks_page.status_code != 200) or ("decks" not in decks_page.url):
      log_error("Failed to login to ankiweb")

    content = decks_page.content

### Use to create local file for testing
#    with open("test.html",'wb') as file:
#      file.write(content)

### Use instead of above code to test everything except logging into and parsing ankiweb
#  with open("test.html","rb") as f:
#    content = f.read()

  return content


### Parse html and sum all due cards
### If there are any nested decks, those due cards will be double counted
def munge_decks_page(decks_page_content: bytes) -> int:
  bs_decks_page = bs(decks_page_content,'html.parser')
  parent_divs = bs_decks_page.find_all('div',{'class':'deckDueNumber'})
  if len(parent_divs) < 2:
    log_error("No decks found on Ankiweb")
  
  reviews_due = 0
  for div in parent_divs:
    reviews_due += int((''.join(div.findAll(text=True)).replace('\n','')))

  return reviews_due

### If appropraite, trigger the IFTTT webhooks endpoint
def send_alert(params: dict, reviews_due: int) -> None:
  if reviews_due > 0:
    ifttt_post_url = ''.join(["https://maker.ifttt.com/trigger/",\
                             params['ifttt_event_name'],"/with/key/",\
                             params['ifttt_event_key']])
    response = post(ifttt_post_url)
    if response.status_code != 200:
      log_error("Failure code returned from ifttt")


def main():
  params = load_config_params(PARAMS_FILE)
  decks_page_content = scrape_ankiweb(params)
  reviews_due = munge_decks_page(decks_page_content)
  send_alert(params, reviews_due)
  log_success(reviews_due)


if __name__ == "__main__":
  main()

