import logging,os
from logging.handlers import RotatingFileHandler
from  config import _current_path,config

__all__ = [
  'logger'
]

__LOG_DIR = f'{_current_path}/logs/'
__LOG_NAME = 'keyword_alert.log'
if config['logger']['path']:
    __LOG_DIR = config['logger']['path'].rstrip('/')

not os.path.exists(__LOG_DIR) and os.makedirs(__LOG_DIR)
__LOG_FILE = f"{__LOG_DIR}/{__LOG_NAME}"
__level = getattr(logging,config['logger']['level']) if hasattr(logging,config['logger']['level']) else 'ERROR'
handler = RotatingFileHandler(__LOG_FILE, maxBytes=5*1024*1024, backupCount=10) # 最大50MB日志
formatter = logging.Formatter(fmt='[%(levelname)s][%(name)s][%(asctime)s]-->%(message)s',datefmt='%Y-%m-%d %H:%M:%S%Z')
handler.setFormatter(formatter)

logger = logging.getLogger('keyword_alert.root')
logger.setLevel(__level)
logger.addHandler(handler)
 
 
