from datetime import datetime as dt
import os 
import sys

from bs4 import BeautifulSoup as bs
from requests import Session,post
import yaml

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE = "{}/history.log".format(DIR_PATH)
PARAMS_FILE = "{}/config_params.yaml".format(DIR_PATH)


def create_timestamp() -> str:
  """Return a string containing timestamp info"""

  now = dt.now()
  unix_timestamp = int(now.timestamp())
  date_string = now.strftime("%Y%m%d")
  time_string = now.strftime("%H:%M:%S")
  return  "{},{},{}".format(unix_timestamp,date_string,time_string)


def log_error(error_msg: str) -> None:
  """Write an error message to the log file and then exit the script."""

  log_string = "{},{}\n".format(create_timestamp(),error_msg)
  with open(LOG_FILE,'a') as file:
    file.write(log_string)
  raise SystemExit


def log_success(reviews_due: int) -> None:
  """Write a line to the log file indicating a successful check."""

  with open(LOG_FILE,'a') as file:
    file.write("{},Review status checked successfully ({})\n".format(create_timestamp(),reviews_due))


def load_config_params(file_name: str) -> dict:
  """Pull in user specific data from parameter file."""

  try:
    with open(file_name) as file:
      params = yaml.load(file, Loader=yaml.FullLoader)
  except IOError:
    log_error("Issue opening or reading from parameters file")

  return params


def scrape_ankiweb(params: dict, test_mode: bool) -> bytes:
  """Login to ankiweb and grab the ankiweb.net/decks page.
     In test mode, use a local copy of the webpage
  """

  ANKI_LOGIN_FORM_POST_URL = 'https://ankiweb.net/account/login'
  ANKI_DECKS_URL = 'https://ankiweb.net/decks/'
  
  
  anki_login_payload = {
    'username': params['anki_username'],
    'password': params['anki_password'],
    'submitted':'1',
    'csrf_token': ''
  }

  if not test_mode:
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
        log_error("Failed to login to ankiweb (Status code: {} URL: {}".format(decks_page.status_code,decks_page.url))

      content = decks_page.content

### Use to create local file for testing
#    with open("test.html",'wb') as file:
#      file.write(content)

  else: # Return a local copy of the webpage so the rest of the script can be tested
    try:
      with open("test.html","rb") as f:
        content = f.read()
    except IOError:
      log_error("Issue opening or reading from test file")

  return content


def munge_decks_page(decks_page_content: bytes) -> int:
  """Parse html and sum all due cards.
  Note: If there are any nested decks, those due cards will be double counted.
  """ 

  bs_decks_page = bs(decks_page_content,'html.parser')
  parent_divs = bs_decks_page.find_all('div',{'class':'deckDueNumber'})
  if len(parent_divs) < 2:
    log_error("No decks found on Ankiweb")
  
  reviews_due = 0
  for div in parent_divs:
    reviews_due += int((''.join(div.findAll(text=True)).replace('\n','')))

  return reviews_due


def send_alert(params: dict, reviews_due: int) -> None:
  """If appropraite, trigger the IFTTT webhooks endpoint."""

  if reviews_due > 0:
    ifttt_post_url = ''.join(["https://maker.ifttt.com/trigger/",\
                             params['ifttt_event_name'],"/with/key/",\
                             params['ifttt_event_key']])
    response = post(ifttt_post_url)
    if response.status_code != 200:
      log_error("Failure code returned from ifttt")


def main():
  args = sys.argv[1:]
  test_mode = False
  if len(args)==1 and args[0]=='test':
    test_mode=True

  params = load_config_params(PARAMS_FILE)
  decks_page_content = scrape_ankiweb(params,test_mode)
  reviews_due = munge_decks_page(decks_page_content)
  send_alert(params, reviews_due)
  log_success(reviews_due)


if __name__ == "__main__":
  main()

