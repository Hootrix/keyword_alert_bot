from telethon import TelegramClient, events, sync, errors
from db import utils
import socks,os,datetime
import re as regex
import diskcache
from urllib.parse import urlparse
from telethon.tl.functions.channels import JoinChannelRequest
import threading
# import pathlib
# import base64
# import tempfile
# from telethon.tl.functions.messages import (GetHistoryRequest)
import yaml

# 配置访问tg服务器的代理
# proxy = (socks.SOCKS5, '127.0.0.1', 1088)
proxy = None

parent_path = os.path.dirname(os.path.realpath(__file__))# 保存数据文件/登录会话信息路径  当前目录
conf_path = parent_path + '/config.yml'
with open(conf_path) as f:
  account = yaml.load(f.read(),Loader = yaml.FullLoader)

cache = diskcache.Cache(parent_path+'/.tmp')# 设置缓存文件目录  当前tmp文件夹

client = TelegramClient('{}/.{}_tg_login'.format(parent_path,account['username']), account['api_id'], account['api_hash'], proxy = proxy)
# client.start(phone=account['phone'])
client.start()


# 设置bot  ，且直接启动
bot = TelegramClient('.{}'.format(account['bot_name']), account['api_id'], account['api_hash'],proxy = proxy).start(bot_token=account['bot_token'])


def js_to_py_re(rx):
  '''
  解析js的正则字符串到python中使用
  只支持ig两个匹配模式
  '''
  query, params = rx[1:].rsplit('/', 1)
  if 'g' in params:
      obj = regex.findall
  else:
      obj = regex.search

  # May need to make flags= smarter, but just an example...    
  return lambda L: obj(query, L, flags=regex.I if 'i' in params else 0)


# 消息读取客户端
# with client:
@client.on(events.NewMessage())
async def on_greeting(event):
    '''Greets someone'''
    # if event.is_group:# 聊天群 类型
    if not event.is_group:# channel 类型
      message = event.message

      text = message.text
      if message.file and message.file.name:
        # text += ' file:{}'.format(message.file.name)# 追加上文件名
        text += ' {}'.format(message.file.name)# 追加上文件名

      # 打印消息
      print(event.chat.id,event.chat.title,event.message.id,text,'\n\n')
      # print( (event.message.get_entities_text()))

      # print( (event.chat.to_dict()))
      # print( (event.message.document))
      # print( (event.message.file))
      
      # 1。失败方法：转发消息 
      # chat = 'keyword_alert_bot' #能转发 但是不能真对特定用户。只能转发给当前允许账户的bot
      # from_chat = 'tianfutong'
      # chat = 349506543# 无法使用chat_id直接转发 没有任何反应
      # chat = 1354871670
      # await message.forward_to('keyword_alert_bot')
      # await client.forward_messages(chat, message)
      # await bot.forward_messages(chat, message)
      # await client.forward_messages(chat, message.id, from_chat)

      # 2.方法：直接发送新消息  而不是转发

      # 查找当前频道的所有订阅
      sql = """
      select u.chat_id,l.keywords
from user_subscribe_list as l  
INNER JOIN user as u on u.id = l.user_id 
where l.channel_name = '{}' and l.status = 0  order by l.create_time  desc
      """.format(event.chat.username)
      find = utils.db.connect.execute_sql(sql).fetchall()
      if find:
        for receiver,keywords in find:
          if regex.search(r'^/.*/[a-zA-Z]*?$',keywords):# 输入的为正则字符串
            regex_match = js_to_py_re(keywords)(text)# 进行正则匹配 只支持ig两个flag
            if isinstance(regex_match,regex.Match):
              regex_match = [regex_match.group()]
            if regex_match:# 正则匹配
              # message = '[found](https://t.me/{}/{}) **{}**\n\nregex: **{}**'.format(event.chat.username,message.id,regex_match,keywords)
              message = '[#FOUND](https://t.me/{}/{}) **{}**'.format(event.chat.username,message.id,regex_match)
              await bot.send_message(receiver, message,link_preview = True,parse_mode = 'markdown')
          else:#普通模式
            if keywords in text:
              message = '[#FOUND](https://t.me/{}/{}) **{}**'.format(event.chat.username,message.id,keywords)
              await bot.send_message(receiver, message,link_preview = True,parse_mode = 'markdown')


# bot相关操作
# with bot:

def parse_url(url):
  """
  解析url信息 
  根据urllib.parse操作 避免它将分号设置为参数的分割符以出现params的问题
  Args:
      url ([type]): [string]
  
  Returns:
      [dict]: [按照个人认为的字段区域名称]  <scheme>://<host>/<uri>?<query>#<fragment>
  """
  res = urlparse(url) # <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
  result = {}
  result['scheme'],result['host'],result['uri'],result['_params'],result['query'],result['fragment'] = list(res)
  if result['_params'] or ';?' in url:
    result['uri'] += ';'+result['_params']
    del result['_params']
  return result



def parse_full_command(command, keywords, channels):
  """
处理多字段的命令参数  拼接合并返回
  Args:
      command ([type]): [命令 如 subscribe  unsubscribe]
      keywords ([type]): [description]
      channels ([type]): [description]

  Returns:
      [type]: [description]
  """
  keywords_list = keywords.split(',')
  channels_list = channels.split(',')
  res = []
  for keyword in keywords_list:
    keyword = keyword.strip()
    for channel in channels_list:
      channel = channel.strip()
      channel = parse_url(channel)['uri'].replace('/','') # 支持传入url  类似 https://t.me/xiaobaiup
      res.append((keyword,channel))
  return res

async def join_channel_insert_subscribe(user_id,keyword_channel_list):
  """
  加入频道 且 写入订阅数据表

  Raises:
      events.StopPropagation: [description]
  """
  res = []

  # 加入频道
  # async def join(c):
  #   await client(JoinChannelRequest(c))
  for k,c in keyword_channel_list:
    try:
      # client.loop.run_until_complete(join(c))
      await client(JoinChannelRequest(c))
      res.append((k,c))
    except Exception as _e: # 不存在的频道
      return '{}频道错误，无法使用\n\nChannel error, unable to use'.format(c)
      pass 
    
  # 写入数据表
  result = []
  for keyword,channel_name in res:
    find = utils.db.user_subscribe_list.get_or_none(**{
      'user_id':user_id,
      'keywords':keyword,
      'channel_name':channel_name,
    })
    if find:
      re_update = utils.db.user_subscribe_list.update(status = 0 ).where(utils.User_subscribe_list.id == find.id)#更新状态
      re_update = re_update.execute()# 更新成功返回1，不管是否重复执行
      if re_update:
        result.append((keyword,channel_name))
    
    else:
      insert_res = utils.db.user_subscribe_list.create(**{
        'user_id':user_id,
        'keywords':keyword,
        'channel_name':channel_name,
        'create_time':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      })
      if insert_res:
        result.append((keyword,channel_name))
      
  return result

def update_subscribe(user_id,keyword_channel_list):
  """
  更新订阅数据表（取消订阅操作）
  """
  
  # 修改数据表
  result = []
  for keyword,channel_name in keyword_channel_list:
    find = utils.db.user_subscribe_list.get_or_none(**{
      'user_id':user_id,
      'keywords':keyword,
      'channel_name':channel_name,
    })
    if find:
      re_update = utils.db.user_subscribe_list.update(status = 1 ).where(utils.User_subscribe_list.id == find)#更新状态
      re_update = re_update.execute()# 更新成功返回1，不管是否重复执行
      if re_update:
        result.append((keyword,channel_name))
    
    else:
      result.append((keyword,channel_name))
  return result



@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
  """Send a message when the command /start is issued."""
  # insert chat_id
  chat_id = event.message.chat.id
  find = utils.db.user.get_or_none(chat_id=chat_id)
  if not find:
    insert_res = utils.db.user.create(**{
      'chat_id':chat_id,
      'create_time':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
  else: # 存在chat_id
    insert_res = True

  if insert_res:
    await event.respond('Hi! Please input /help , access usage.')
  else:
    await event.respond('Opps! Please try again /start ')
  
  raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/subscribe'))
async def subscribe(event):
  """Send a message when the command /subscribe is issued."""
  # insert chat_id
  chat_id = event.message.chat.id
  find = utils.db.user.get_or_none(chat_id=chat_id)
  user_id = find
  if not find:# 不存在用户信息
    await event.respond('Failed. Please input /start')
    raise events.StopPropagation
  
  text = event.message.text
  text = text.replace('，',',')# 替换掉中文逗号
  text = regex.sub('\s*,\s*',',',text) # 确保英文逗号间隔中间都没有空格  如 "https://t.me/xiaobaiup, https://t.me/com9ji"
  splitd = [i for i in regex.split('\s+',text) if i]# 删除空元素
  if len(splitd) <= 1:
    await event.respond('输入需要订阅的关键字,支持js正则语法：`/.../ig`\n\nInput the keyword that needs to subscribe, support JS regular syntax：`/.../ig`')
    cache.set('status_{}'.format(chat_id),{'current_status':'/subscribe keywords','record_value':text},expire=5*60)#设置5m后过期
  elif len(splitd)  == 3:
    command, keywords, channels = splitd
    result = await join_channel_insert_subscribe(user_id,parse_full_command(command, keywords, channels))
    if isinstance(result,str): await event.respond(result,parse_mod = None)
    msg = ''
    for key,channel in result:
      msg += '{},{}\n'.format(key,channel)
    if msg:
      await event.respond('success:\n'+msg,parse_mode = None)

  raise events.StopPropagation


@bot.on(events.NewMessage(pattern='/unsubscribe_all'))
async def unsubscribe_all(event):
  """Send a message when the command /unsubscribe_all is issued."""
  # insert chat_id
  chat_id = event.message.chat.id
  find = utils.db.user.get_or_none(chat_id=chat_id)
  if not find:# 不存在用户信息
    await event.respond('Failed. Please input /start')
    raise events.StopPropagation
  user_id = find.id
  
  # 查找当前的订阅数据
  _user_subscribe_list = utils.db.connect.execute_sql('select keywords,channel_name from user_subscribe_list where user_id = %d and status  = %d' % (user_id,0) ).fetchall()
  if _user_subscribe_list:
    msg = ''
    for keywords,channel_name in _user_subscribe_list:
      msg += 'keyword: {}\nchannel: https://t.me/{}\n---\n'.format(keywords,channel_name)

    re_update = utils.db.user_subscribe_list.update(status = 1 ).where(utils.User_subscribe_list.user_id == user_id)#更新状态
    re_update = re_update.execute()# 更新成功返回1，不管是否重复执行
    if re_update:
      await event.respond('success unsubscribe_all:\n' + msg,link_preview = False,parse_mode = None)
  else:
    await event.respond('not found unsubscribe list')
  raise events.StopPropagation


@bot.on(events.NewMessage(pattern='/unsubscribe'))
async def unsubscribe(event):
  """Send a message when the command /unsubscribe is issued."""
  # insert chat_id
  chat_id = event.message.chat.id
  find = utils.db.user.get_or_none(chat_id=chat_id)
  user_id = find
  if not find:# 不存在用户信息
    await event.respond('Failed. Please input /start')
    raise events.StopPropagation
  

  text = event.message.text
  text = text.replace('，',',')# 替换掉中文逗号
  text = regex.sub('\s*,\s*',',',text) # 确保英文逗号间隔中间都没有空格  如 "https://t.me/xiaobaiup, https://t.me/com9ji"
  splitd = [i for i in regex.split('\s+',text) if i]# 删除空元素
  if len(splitd) <= 1:
    await event.respond('输入需要**取消订阅**的关键字\n\nEnter a keyword that requires **unsubscribe**')
    cache.set('status_{}'.format(chat_id),{'current_status':'/unsubscribe keywords','record_value':text},expire=5*60)#设置5m后过期
  elif len(splitd)  == 3:
    command, keywords, channels = splitd
    result = update_subscribe(user_id,parse_full_command(command, keywords, channels))
    msg = ''
    for key,channel in result:
      msg += '{},{}\n'.format(key,channel)
    if msg:
      await event.respond('success:\n'+msg,parse_mode = None)

  raise events.StopPropagation


@bot.on(events.NewMessage(pattern='/help'))
async def start(event):
  await event.respond('''

目的：根据关键字订阅频道消息

支持多关键字和多频道订阅，使用英文逗号`,`间隔

关键字和频道之间使用空格间隔

主要命令：

/subscribe - 订阅操作： `关键字1,关键字2 https://t.me/tianfutong,https://t.me/xiaobaiup`

/unsubscribe - 取消订阅： `关键字1,关键字2 https://t.me/tianfutong,https://t.me/xiaobaiup`

/unsubscribe_all - 取消所有订阅

/list - 显示所有订阅列表

---

Purpose: Subscribe to channel messages based on keywords

Multi-keyword and multi-channel subscription support, using comma `,` interval.

Use space between keywords and channels

Main command:

/subscribe - Subscription operation: `keyword1,keyword2 https://t.me/tianfutong,https://t.me/xiaobaiup`

/unsubscribe - unsubscribe: `keyword1,keyword2 https://t.me/tianfutong,https://t.me/xiaobaiup`

/unsubscribe_all - cancel all subscriptions

/list - displays a list of all subscriptions

  ''')
  raise events.StopPropagation


# 删除当前记录的用户状态
@bot.on(events.NewMessage(pattern='/cancel'))
async def cancel(event):
  chat_id = event.message.chat.id
  _ = cache.delete('status_{}'.format(chat_id))
  if _ :
    await event.respond('success.')
  raise events.StopPropagation

# 查询当前用户的所有订阅
@bot.on(events.NewMessage(pattern='/list'))
async def _list(event):
  chat_id = event.message.chat.id
  find = utils.db.user.get_or_none(**{
      'chat_id':chat_id,
  })
  if find:
    find = utils.db.connect.execute_sql('select keywords,channel_name from user_subscribe_list where user_id = %d and status  = %d' % (find.id,0) ).fetchall()
    if find:
      msg = ''
      # msg = 'list:\n'
      for keywords,channel_name in find:
        msg += 'keyword: {}\nchannel: https://t.me/{}\n---\n'.format(keywords,channel_name)
      await event.respond(msg,parse_mode = None) # 不用任何模式解析 直接输出显示
    else:
      await event.respond('not found list')
  else:
    await event.respond('please /start')
  raise events.StopPropagation


# 其余的消息统一回复（复读机）
@bot.on(events.NewMessage)
async def echo(event):
  """Echo the user message."""
  chat_id = event.message.chat.id
  text = event.text
  text = text.replace('，',',')# 替换掉中文逗号
  text = regex.sub('\s*,\s*',',',text) # 确保英文逗号间隔中间都没有空格  如 "https://t.me/xiaobaiup, https://t.me/com9ji"

  find = cache.get('status_{}'.format(chat_id))
  if find:

    # 执行订阅
    if find['current_status'] == '/subscribe keywords':# 当前输入关键字
      await event.respond('输入需要订阅的频道url或者name：\n\nEnter the url or name of the channel to subscribe to:')
      cache.set('status_{}'.format(chat_id),{'current_status':'/subscribe channels','record_value':find['record_value'] + ' ' + text},expire=5*60)# 记录输入的关键字
      raise events.StopPropagation
    elif find['current_status'] == '/subscribe channels':# 当前输入频道
      full_command = find['record_value'] + ' ' + text
      splitd = [i for i in regex.split('\s+',full_command) if i]# 删除空元素
      command, keywords, channels = splitd
      user_id = utils.db.user.get_or_none(chat_id=chat_id)
      result = await join_channel_insert_subscribe(user_id,parse_full_command(command, keywords, channels))
      if isinstance(result,str): await event.respond(result,parse_mod = None)
      msg = ''
      for key,channel in result:
        msg += '{},{}\n'.format(key,channel)
      if msg:
        await event.respond('success:\n'+msg,parse_mode = None)

      cache.delete('status_{}'.format(chat_id))
      raise events.StopPropagation
    
    #取消订阅
    elif find['current_status'] == '/unsubscribe keywords':# 当前输入关键字
      await event.respond('输入需要**取消订阅**的频道url或者name：\n\nEnter the url or name of the channel where ** unsubscribe **is required:')
      cache.set('status_{}'.format(chat_id),{'current_status':'/unsubscribe channels','record_value':find['record_value'] + ' ' + text},expire=5*60)# 记录输入的关键字
      raise events.StopPropagation
    elif find['current_status'] == '/unsubscribe channels':# 当前输入频道
      full_command = find['record_value'] + ' ' + text
      splitd = [i for i in regex.split('\s+',full_command) if i]# 删除空元素
      command, keywords, channels = splitd
      user_id = utils.db.user.get_or_none(chat_id=chat_id)
      result = update_subscribe(user_id,parse_full_command(command, keywords, channels))
      msg = ''
      for key,channel in result:
        msg += '{},{}\n'.format(key,channel)
      if msg:
        await event.respond('success:\n'+msg,parse_mode = None)

      cache.delete('status_{}'.format(chat_id))
      raise events.StopPropagation

  # print(chat_id)
  # await event.respond('repeat: '+event.text)
  raise events.StopPropagation


# bot发送消息给用户
async def send_message(chat_id,forward_message = None):
  try:
    if forward_message:
      await bot.forward_messages(chat_id, forward_message)
    else:
      await bot.send_message(chat_id, 'test message ')# 发送测试消息

  except errors.rpcerrorlist.UserIsBlockedError  as _e:
    print(_e)  # User is blocked (caused by SendMessageRequest)  用户已手动停止bot
    pass # 关闭全部订阅
  except ValueError  as _e:
    # print(_e)  # 用户从未使用bot
    # 删除用户订阅和id
    isdel = utils.db.user.delete().where(utils.User.chat_id == chat_id).execute()
    user_id = utils.db.user.get_or_none(chat_id=chat_id)
    if user_id:
      isdel2 = utils.db.user_subscribe_list.delete().where(utils.User_subscribe_list.user_id == user_id.id).execute()
    # if isdel:# 删除成功
    #   pass 



if __name__ == "__main__":
    # 手动开启bot机器人loop。上面start已经启动了
    # def bot_loop_worker():
    #   print('bot started')
    #   bot.run_until_disconnected()
    # account_worker = threading.Thread(target=bot_loop_worker,daemon=True,name='bot_loop_worker')
    # account_worker.start()

    # 开启client loop
    client.run_until_disconnected()
  
# test
# async def main():
#     # You can print the message history of any chat:
#     # async for message in client.iter_messages('tianfutong'):
#     # async for message in client.iter_messages('pdf_001'):
#     #   text = message.text
#     #   if message.file and message.file.name:
#     #     text += ' file:{}'.format(message.file.name)
#     #   print(message.id, text)

#         # You can download media from messages, too!
#         # The method will return the path where the file was saved.
#         # if message.photo:
#         #     path = await message.download_media()
#         #     print('File saved to', path)  # printed after download is done

