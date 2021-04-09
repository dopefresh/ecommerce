import easypost

import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

easypost.api_key = os.environ['EASY_POST_API_KEY']
print(easypost.api_key)
