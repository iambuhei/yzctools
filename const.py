from configparser import ConfigParser

config = ConfigParser()
if config.read('config.ini'):
    API_URL = config['osu_api']['url']
    API_KEY = config['osu_api']['key']
    PATH_CSV_SAVE = config['path']['csv_save']
else:
    raise FileNotFoundError('File config.ini does not exist.')
