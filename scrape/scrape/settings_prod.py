from scrape.settings_base import *
from collabovid_settings.postgres_settings import *
from collabovid_settings.tasks_settings import *

if int(os.getenv('ALLOW_IMAGE_SCRAPING', 0)) > 0:
    ALLOW_IMAGE_SCRAPING = True
else:
    ALLOW_IMAGE_SCRAPING = False