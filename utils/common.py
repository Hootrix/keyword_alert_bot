from config import config
from colorama import Fore, Style, init
from text_box_wrapper import wrap
from .__version__ import __version__


def is_allow_access(chat_id) -> bool:
  '''
  检查当前chat_id有权限使用bot

  Args:
      chat_id (_type_): Telegram chat id

  Returns:
      bool: 是否允许使用
  '''
  # 非公共服务
  if 'private_service' in config and config['private_service']:
    if 'authorized_users' in config:
      # 只服务指定的用户
      if chat_id in config['authorized_users']:
          return True
    return False
  return True

def read_tag_from_file(filename="version.txt"):
  '''
  获取tag信息  
  Args:
      filename (str, optional): _description_. Defaults to "version.txt".

  Returns:
      _type_: _description_
  '''
  return __version__
  # try:
  #     with open(filename, "r") as f:
  #         tag = f.read().strip()
  # except FileNotFoundError:
  #     tag = "unknown"
  # return tag

@wrap(border_string='##',min_padding=2)
def banner():
  init()  # 初始化colorama
  green_circle = f"{Fore.GREEN}● success{Style.RESET_ALL}\n"
  tag = read_tag_from_file()
  message = f"{green_circle} 🤖️Telegram keyword alert bot (Version: {tag})"
  return message