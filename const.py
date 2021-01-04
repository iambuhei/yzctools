from configparser import ConfigParser
import json

config = ConfigParser()
if config.read('config.ini'):
    API_URL = config['osu_api']['url']
    API_KEY = config['osu_api']['key']
    PATH_CSV_SAVE = config['path']['csv_save']
    PATH_USERNAME = config['path']['usernames_json']
else:
    raise FileNotFoundError('File config.ini does not exist.')

with open(PATH_USERNAME, 'r') as load_f:
    USERNAMES_DICT = json.load(load_f)
