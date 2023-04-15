from config import config

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