import os
from dotenv import load_dotenv
load_dotenv('.env')
db_url = os.getenv('DATABASE_URL', '')
print('DATABASE_URL from environment:', db_url)
print ('Expected prefix: postgresql ://')
expected_prefix = 'postgresql : //'
actual_prefix = db_url[:len(expected_prefix)]
print('Actual prefix:', actual_prefix)
print('Is correct format?', actual_prefix == expected_prefix)