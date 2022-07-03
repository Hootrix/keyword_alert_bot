#coding=utf-8
from telethon import TelegramClient, events, sync, errors
from db import utils
import socks,os,datetime
import re as regex
import diskcache
import time
from urllib.parse import urlparse
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import DeleteHistoryRequest
from telethon.tl.functions.channels import LeaveChannelRequest, DeleteChannelRequest
from logger import logger
from config import config,_current_path as current_path
from telethon import utils as telethon_utils
from telethon.tl.types import PeerChannel
from telethon.extensions import markdown,html


PRODUCTION = False # 是否为生产环境（无代理配置）

# 配置访问tg服务器的代理
proxy = None
if all(config['proxy'].values()): # 同时不为None
  logger.info(f'proxy info:{config["proxy"]}')
  proxy = (getattr(socks,config['proxy']['type']), config['proxy']['address'], config['proxy']['port'])
# proxy = (socks.SOCKS5, '127.0.0.1', 1088)
else:
  PRODUCTION = True # 生产环境会退出无用的频道/群组

account = config['account']
cache = diskcache.Cache(current_path+'/.tmp')# 设置缓存文件目录  当前tmp文件夹。用于缓存分步执行命令的操作，避免bot无法找到当前输入操作的进度
client = TelegramClient('{}/.{}_tg_login'.format(current_path,account['username']), account['api_id'], account['api_hash'], proxy = proxy)
client.start(phone=account['phone'])
# client.start()

# 设置bot，且直接启动
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

def is_regex_str(string):
  return regex.search(r'^/.*/[a-zA-Z]*?$',string)

# client相关操作 目的：读取消息
@client.on(events.MessageEdited)
@client.on(events.NewMessage())
async def on_greeting(event):
    '''Greets someone'''
    # telethon.events.newmessage.NewMessage.Event
    # telethon.events.messageedited.MessageEdited.Event
    if not event.chat:
      logger.error(f'event.chat empty. event.chat: { event.chat }')
      raise events.StopPropagation

    if event.chat.username == account['bot_name']: # 不监听当前机器人消息
      logger.debug(f'不监听当前机器人消息, event.chat.username: { event.chat.username }')
      raise events.StopPropagation

    sender_username = event.message.sender.username if event.message.sender.username is not None else '' 
    if sender_username.lower().endswith('bot'): # 不监听所有机器人发的消息
      logger.debug(f'不监听所有机器人消息, event.chat.username: { event.chat.username }')
      raise events.StopPropagation      
      
    # if not event.is_group:# channel 类型
    if True:# 所有消息类型，支持群组
      message = event.message

      text = message.text
      if message.file and message.file.name:
        # text += ' file:{}'.format(message.file.name)# 追加上文件名
        text += ' {}'.format(message.file.name)# 追加上文件名

      # 打印消息
      logger.debug(f'event.chat.username: {event.chat.username},event.chat.id:{event.chat.id},event.chat.title:{event.chat.title},event.message.id:{event.message.id},text:{text}')
      
      # 1.方法(失败)：转发消息 
      # chat = 'keyword_alert_bot' #能转发 但是不能真对特定用户。只能转发给当前允许账户的bot
      # from_chat = 'tianfutong'
      # chat = 349506543# 无法使用chat_id直接转发 没有任何反应
      # chat = 1354871670
      # await message.forward_to('keyword_alert_bot')
      # await client.forward_messages(chat, message)
      # await bot.forward_messages(chat, message)
      # await client.forward_messages(chat, message.id, from_chat)

      # 2.方法：直接发送新消息,非转发.但是可以url预览达到效果

      # 查找当前频道的所有订阅
      sql = """
select u.chat_id,l.keywords,l.id,l.chat_id
from user_subscribe_list as l  
INNER JOIN user as u on u.id = l.user_id 
where (l.channel_name = ? or l.chat_id = ?)  and l.status = 0  order by l.create_time  desc
      """
      find = utils.db.connect.execute_sql(sql,(event.chat.username,str(event.chat_id))).fetchall()
      if find:
        logger.info(f'channel: {event.chat.username}; all chat_id & keywords:{find}') # 打印当前频道，订阅的用户以及关键字
        for receiver,keywords,l_id,l_chat_id in find:
          try:

            # 消息发送去重KEY（diskcache支持原子操作）
            # 唯一性：user_chat_id，订阅列表id。
            # 若重复订阅允许重复推送
            # 配合后面5秒cache, 可以使得短时间内重复刷屏的消息只推送一次
            CACHE_KEY_UNIQUE_SEND = f'{receiver}_{l_id}' 

            # 配合后面5秒cache, 实现若一条消息匹配多个判断条件, 只发送一次
            CACHE_MSG_UNIQUE_SEND = f'{receiver}_{message.id}'

            # 优先返回可预览url
            channel_url = f'https://t.me/{event.chat.username}/' if event.chat.username else get_channel_url(event.chat.username,event.chat_id)
            channel_msg_url= f'{channel_url}{message.id}'
            send_cache_key = f'_LAST_{l_id}_{message.id}_send'
            if isinstance(event,events.MessageEdited.Event):# 编辑事件
              # 24小时内新建2秒后的编辑不提醒
              if cache.get(send_cache_key) and (event.message.edit_date - event.message.date) > datetime.timedelta(seconds=2): 
                logger.error(f'{channel_msg_url} repeat send. deny!')
                continue

            if not l_chat_id:# 未记录频道id
              logger.info(f'update user_subscribe_list.chat_id:{event.chat_id}  where id = {l_id} ')
              re_update = utils.db.user_subscribe_list.update(chat_id = str(event.chat_id) ).where(utils.User_subscribe_list.id == l_id)
              re_update.execute()
            
            chat_title = f'{event.chat.title}' if event.chat.title is not None else ""
            channel_title = f" CHANNEL: {chat_title}"

            if is_regex_str(keywords):# 输入的为正则字符串
              regex_match = js_to_py_re(keywords)(text)# 进行正则匹配 只支持ig两个flag
              if isinstance(regex_match,regex.Match):#search()结果
                regex_match = [regex_match.group()]
              regex_match_str = []# 显示内容
              for _ in regex_match:
                item = ''.join(_) if isinstance(_,tuple) else _
                if item:
                  regex_match_str.append(item) # 合并处理掉空格
              regex_match_str = list(set(regex_match_str))# 处理重复元素
              if regex_match_str:# 默认 findall()结果
                # # {chat_title} \n\n
                message_str = f'[#FOUND]({channel_msg_url}) **{regex_match_str}** in {channel_title} by @{sender_username}'
                if cache.add(CACHE_KEY_UNIQUE_SEND,1,expire=5) and cache.add(CACHE_MSG_UNIQUE_SEND,1,expire=5):
                  logger.info(f'REGEX: receiver chat_id:{receiver}, l_id:{l_id}, message_str:{message_str}')
                  if isinstance(event,events.NewMessage.Event):# 新建事件
                    cache.set(send_cache_key,1,expire=86400) # 发送标记缓存一天
                  await bot.send_message(receiver, message_str,link_preview = True,parse_mode = 'markdown')
                else:
                  # 已发送该消息
                  logger.error(f'REGEX send repeat. {receiver}_{l_id}:{channel_url}')
                  continue

              else:
                logger.debug(f'regex_match empty. regex:{keywords} ,message: t.me/{event.chat.username}/{event.message.id}')
            else:#普通模式
              if keywords in text:
                # # {chat_title} \n\n
                message_str = f'[#FOUND]({channel_msg_url}) **{keywords}** in {channel_title} by @{sender_username}'
                if cache.add(CACHE_KEY_UNIQUE_SEND,1,expire=5) and cache.add(CACHE_MSG_UNIQUE_SEND,1,expire=5):
                  logger.info(f'TEXT: receiver chat_id:{receiver}, l_id:{l_id}, message_str:{message_str}')
                  if isinstance(event,events.NewMessage.Event):# 新建事件
                    cache.set(send_cache_key,1,expire=86400) # 发送标记缓存一天
                  await bot.send_message(receiver, message_str,link_preview = True,parse_mode = 'markdown')
                else:
                  # 已发送该消息
                  logger.error(f'TEXT send repeat. {receiver}_{l_id}:{channel_url}')
                  continue

          except errors.rpcerrorlist.UserIsBlockedError  as _e:
            # User is blocked (caused by SendMessageRequest)  用户已手动停止bot
            logger.error(f'{_e}')
            pass # 关闭全部订阅
          except ValueError  as _e:
            # 用户从未使用bot
            logger.error(f'{_e}')
            # 删除用户订阅和id
            isdel = utils.db.user.delete().where(utils.User.chat_id == receiver).execute()
            user_id = utils.db.user.get_or_none(chat_id=receiver)
            if user_id:
              isdel2 = utils.db.user_subscribe_list.delete().where(utils.User_subscribe_list.user_id == user_id.id).execute()
          except Exception as _e:
            logger.error(f'{_e}')
      else:
        logger.debug(f'sql find empty. event.chat.username:{event.chat.username}, find:{find}, sql:{sql}')

        # 暂停频道退出操作
        # if PRODUCTION:
        #   logger.info(f'Leave  Channel/group: {event.chat.username}')
        #   await leave_channel(event.chat.username)


# bot相关操作
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

def get_channel_url(event_chat_username,event_chat__id):
  """
  获取频道/群组 url
  优先返回chat_id的url

  https://docs.telethon.dev/en/latest/concepts/chats-vs-channels.html#converting-ids

  Args:
      event_chat_username (str): 频道名地址 e.g. tianfutong 
      event_chat__id (str): 频道的非官方id。 e.g. -1001630956637
  """
  # event.is_private 无法判断
  # 判断私有频道
  # is_private = True if not event_chat_username else False
  host = 'https://t.me/'
  url = ''
  if event_chat__id:
    real_id, peer_type = telethon_utils.resolve_id(int(event_chat__id)) # 转换为官方真实id
    url = f'{host}c/{real_id}/'
  elif event_chat_username:
    url = f'{host}{event_chat_username}/'
  return url


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

  支持传入频道id

  Raises:
      events.StopPropagation: [description]
  """
  res = []
  # 加入频道
  for k,c in keyword_channel_list:
    username = ''
    chat_id = ''
    try:
      if c.lstrip('-').isdigit():# 整数
        real_id, peer_type = telethon_utils.resolve_id(int(c))
        channel_entity = await client.get_entity(real_id)
        chat_id = telethon_utils.get_peer_id(PeerChannel(real_id)) # 转换为marked_id 
        # channel_entity.title
      else:# 传入普通名称
        channel_entity = await client.get_entity(c) # get_entity频繁请求会有报错 A wait of 19964 seconds is required (caused by ResolveUsernameRequest)
        chat_id = telethon_utils.get_peer_id(PeerChannel(channel_entity.id)) # 转换为marked_id 
      
      if channel_entity.username: username = channel_entity.username
      
      if channel_entity and not channel_entity.left: # 已加入该频道
        res.append((k,username,chat_id))
      else:
        await client(JoinChannelRequest(channel_entity))
        res.append((k,username,chat_id))
    except Exception as _e: # 不存在的频道
      logger.error(f'{c} JoinChannelRequest ERROR:{_e}')
      
      # 查询本地记录是否存在
      channel_name_or_chat_id = regex.sub(r'^(?:http[s]?://)?t.me/(?:c/)?','',c) # 清洗多余信息
      find = utils.db.connect.execute_sql('select 1 from user_subscribe_list where status = 0 and (channel_name = ? or chat_id = ?)' ,(channel_name_or_chat_id,channel_name_or_chat_id)).fetchall()
      logger.warning(f'{c} JoinChannelRequest fail. cache join. cache find count: {len(find)}')
      if find:
        if len(find) > 1: # 存在1条以上的记录 则直接返回加入成功
          if channel_name_or_chat_id.lstrip('-').isdigit():# 整数
            res.append((k,'',channel_name_or_chat_id))
          else:
            res.append((k,channel_name_or_chat_id,''))
        else:
          return '无法使用该频道：{}\n\nChannel error, unable to use: {}'.format(c,_e)
      else:
        return '无法使用该频道：{}\n\nChannel error, unable to use: {}'.format(c,_e)
    
  # 写入数据表
  result = []
  for keyword,channel_name,_chat_id in res:
    find = utils.db.user_subscribe_list.get_or_none(**{
        'user_id':user_id,
        'keywords':keyword,
        'channel_name':channel_name,
        'chat_id':_chat_id,
      })

    if find:
      re_update = utils.db.user_subscribe_list.update(status = 0 ).where(utils.User_subscribe_list.id == find.id)#更新状态
      re_update = re_update.execute()# 更新成功返回1，不管是否重复执行
      if re_update:
        result.append((keyword,channel_name,_chat_id))
    else:
      insert_res = utils.db.user_subscribe_list.create(**{
        'user_id':user_id,
        'keywords':keyword,
        'channel_name':channel_name.replace('@',''),
        'create_time':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'chat_id':_chat_id
      })
      if insert_res:
        result.append((keyword,channel_name,_chat_id))
  return result

async def leave_channel(channel_name):
  '''
  退出无用的频道/组

  Args:
      channel_name ([type]): [description]
  '''
  try:
      await client(LeaveChannelRequest(channel_name))
      await client(DeleteChannelRequest(channel_name))
      await client(DeleteHistoryRequest(channel_name))
      logger.info(f'退出 {channel_name}')
  except Exception as _e: # 不存在的频道
      return f'无法退出该频道：{channel_name}, {_e}'
      

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
    await event.respond('输入需要订阅的关键字,支持js正则语法：`/[\s\S]*/ig`\n\nInput the keyword that needs to subscribe, support JS regular syntax：`/[\s\S]*/ig`')
    cache.set('status_{}'.format(chat_id),{'current_status':'/subscribe keywords','record_value':text},expire=5*60)#设置5m后过期
  elif len(splitd)  == 3:
    command, keywords, channels = splitd
    result = await join_channel_insert_subscribe(user_id,parse_full_command(command, keywords, channels))
    if isinstance(result,str): 
        logger.error('join_channel_insert_subscribe 错误：'+result)
        await event.respond(result,parse_mode = None) # 提示错误消息
    else:
      msg = ''
      for key,channel,_chat_id in result:
        if _chat_id:
          _chat_id, peer_type = telethon_utils.resolve_id(int(_chat_id))
        msg += 'keyword:{}  channel:{}\n'.format(key,(channel if channel else f't.me/c/{_chat_id}'))
      if msg:
        # await event.respond('success subscribe:\n'+msg,parse_mode = None)
        await event.respond('success subscribe: {}'.format(channel if channel else f't.me/c/{_chat_id}'), parse_mode = None)
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
  _user_subscribe_list = utils.db.connect.execute_sql('select keywords,channel_name,chat_id from user_subscribe_list where user_id = %d and status  = %d' % (user_id,0) ).fetchall()
  if _user_subscribe_list:
    msg = ''
    for keywords,channel_name,chat_id in _user_subscribe_list:
      channel_url = get_channel_url(channel_name,chat_id)
      msg += 'keyword: {}\nchannel: {}\n---\n'.format(keywords,channel_url)

    re_update = utils.db.user_subscribe_list.update(status = 1 ).where(utils.User_subscribe_list.user_id == user_id)#更新状态
    re_update = re_update.execute()# 更新成功返回1，不管是否重复执行
    if re_update:
      await event.respond('success unsubscribe_all:\n' + msg,link_preview = False,parse_mode = None)
  else:
    await event.respond('not found unsubscribe list')
  raise events.StopPropagation


@bot.on(events.NewMessage(pattern='/unsubscribe_id'))
async def unsubscribe_id(event):
  '''
  根据id取消订阅
  '''
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
  if len(splitd) > 1:
    ids = [int(i) for i in splitd[1].split(',')]
    result = []
    for i in ids:
      re_update = utils.db.user_subscribe_list.update(status = 1 ).where(utils.User_subscribe_list.id == i,utils.User_subscribe_list.user_id == user_id)#更新状态
      re_update = re_update.execute()# 更新成功返回1，不管是否重复执行
      if re_update:
        result.append(i)
    await event.respond('success unsubscribe id:{}'.format(result if result else 'None'))
  elif len(splitd) < 2:
    await event.respond('输入需要**取消订阅**的订阅id：\n\nEnter the subscription id of the channel where ** unsubscribe **is required:')
    cache.set('status_{}'.format(chat_id),{'current_status':'/unsubscribe_id ids','record_value':None},expire=5*60)# 记录输入的关键字
    raise events.StopPropagation
  else:
    await event.respond('not found id')
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
    # msg = ''
    # for key,channel in result:
    #   msg += 'keyword:{}  channel:{}\n'.format(key,channel)
    # if msg:
    #   await event.respond('success unsubscribe:\n'+msg,parse_mode = None)
    await event.respond('success unsubscribe.')

  raise events.StopPropagation


@bot.on(events.NewMessage(pattern='/help'))
async def start(event):
  await event.respond('''

目的：根据关键字订阅频道消息，支持群组

BUG反馈：https://git.io/JJ0Ey

支持多关键字和多频道订阅，使用英文逗号`,`间隔

关键字和频道之间使用空格间隔

主要命令：

 - 订阅操作

  /subscribe  关键字1,关键字2 tianfutong,xiaobaiup

  /subscribe  关键字1,关键字2 https://t.me/tianfutong,https://t.me/xiaobaiup

 - 取消订阅

  /unsubscribe  关键字1,关键字2 https://t.me/tianfutong,https://t.me/xiaobaiup

 - 取消订阅id

  /unsubscribe_id  1,2

 - 取消所有订阅

  /unsubscribe_all

 - 显示所有订阅列表

  /list

---
Purpose: Subscribe to channel messages based on keywords. Support groups

BUG FEEDBACK: https://git.io/JJ0Ey

Multi-keyword and multi-channel subscription support, using comma `,` interval.

Use space between keywords and channels

Main command:

/subscribe  keyword1,keyword2 tianfutong,xiaobaiup
/subscribe  keyword1,keyword2 https://t.me/tianfutong,https://t.me/xiaobaiup

/unsubscribe  keyword1,keyword2 https://t.me/tianfutong,https://t.me/xiaobaiup

/unsubscribe_id  1,2

/unsubscribe_all

/list

  ''')
  raise events.StopPropagation


# 删除当前记录的用户状态
@bot.on(events.NewMessage(pattern='/cancel'))
async def cancel(event):
  chat_id = event.message.chat.id
  _ = cache.delete('status_{}'.format(chat_id))
  if _ :
    await event.respond('success cancel.')
  raise events.StopPropagation

# 查询当前用户的所有订阅
@bot.on(events.NewMessage(pattern='/list'))
async def _list(event):
  chat_id = event.message.chat.id
  find = utils.db.user.get_or_none(**{
      'chat_id':chat_id,
  })
  if find:
    find = utils.db.connect.execute_sql('select id,keywords,channel_name,chat_id from user_subscribe_list where user_id = %d and status  = %d' % (find.id,0) ).fetchall()
    if find:
      msg = ''
      for sub_id,keywords,channel_name,chat_id in find:
        _type = 'regex' if is_regex_str(keywords) else 'keyword'
        channel_url = get_channel_url(channel_name,chat_id)
        
        channel_entity = None # TODO 不执行实体信息读取  否则会无响应
        # _entity = int(chat_id) if chat_id else channel_name
        # # channel_entity1 = await client.get_entity('tianfutong')
        # # channel_entity2 = await client.get_entity('@tianfutong')
        # # channel_entity3 = await client.get_entity(-1001242421091)
        # # channel_entity4 = await client.get_entity(1242421091)
        # try:
        #   channel_entity = await client.get_entity(_entity)# 获取频道相关信息
        # except ValueError as _e:# 频道不存在报错
        #   pass
        #   # logger.info(f'delete user_subscribe_list channel id:{sub_id} _entity:{_entity}')
        #   # re_update = utils.db.user_subscribe_list.update(status = 1 ).where(utils.User_subscribe_list.id == sub_id)
        #   # re_update.execute()
        #   class channel_entity: username='';title=''

        channel_title = ''
        if channel_entity and channel_entity.title:channel_title = f'channel title: {channel_entity.title}\n'
        
        if channel_name:
          if channel_entity:
            if channel_entity.username:
              if channel_entity.username != channel_name:
                channel_name += '\t[CHANNEL NAME EXPIRED]'# 标记频道名称过期
                # channel_name = '' # 不显示
                logger.info(f'channel username:{channel_name} expired.')
            else:
              channel_name += '\t[CHANNEL NONE EXPIRED]'# 标记频道名称过期.当前不存在
              # channel_name = '' # 不显示
              logger.info(f'channel username:{channel_name} expired. current none')
        elif chat_id:# 只有chat_id
          if channel_entity and channel_entity.username:
            channel_name = channel_entity.username
            logger.info(f'channel chat_id:{chat_id} username:{channel_name}')

        channel_username = ''
        if channel_entity:# 有实体信息才显示频道名
          if channel_name:
            channel_username = f'channel username: {channel_name}\n'

        channel_url = f'<a href="{channel_url}">{"https://t.me/"+channel_name if channel_name else channel_url}</a>'
        msg += f'id:{sub_id}\n{_type}: {keywords}\n{channel_title}{channel_username}channel url: {channel_url}\n---\n'
      
      text, entities = html.parse(msg)# 解析超大文本 分批次发送 避免输出报错
      for text, entities in telethon_utils.split_text(text, entities):
        # await client.send_message(chat, text, formatting_entities=entities)
        await event.respond(text,formatting_entities=entities) 
    else:
      await event.respond('not found list')
  else:
    await event.respond('please /start')
  raise events.StopPropagation


# 其余消息的统一处理方法
@bot.on(events.NewMessage)
async def common(event):
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
      if len(splitd)  != 3:
        await event.respond('关键字请不要包含空格 可使用正则表达式解决\n\nThe keyword must not contain Spaces.')
        raise events.StopPropagation
      command, keywords, channels = splitd
      user_id = utils.db.user.get_or_none(chat_id=chat_id)
      result = await join_channel_insert_subscribe(user_id,parse_full_command(command, keywords, channels))
      if isinstance(result,str): 
        await event.respond(result,parse_mode = None) # 提示错误消息
      else:
        msg = ''
        for key,channel,_chat_id in result:
          if _chat_id:
            _chat_id, peer_type = telethon_utils.resolve_id(int(_chat_id))
          msg += 'keyword:{}  channel:{}\n'.format(key,(channel if channel else f't.me/c/{_chat_id}'))
        if msg:
          # await event.respond('success subscribe:\n'+msg,parse_mode = None)
          await event.respond('success subscribe: {}'.format(channel if channel else f't.me/c/{_chat_id}'), parse_mode = None)

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
      if len(splitd)  != 3:
        await event.respond('关键字请不要包含空格 可使用正则表达式解决\n\nThe keyword must not contain Spaces.')
        raise events.StopPropagation
      command, keywords, channels = splitd
      user_id = utils.db.user.get_or_none(chat_id=chat_id)
      result = update_subscribe(user_id,parse_full_command(command, keywords, channels))
      # msg = ''
      # for key,channel in result:
      #   msg += '{},{}\n'.format(key,channel)
      # if msg:
      #   await event.respond('success:\n'+msg,parse_mode = None)
      await event.respond('success unsubscribe..')

      cache.delete('status_{}'.format(chat_id))
      raise events.StopPropagation
    elif find['current_status'] == '/unsubscribe_id ids':# 当前输入订阅id
      splitd =  text.strip().split(',')
      user_id = utils.db.user.get_or_none(chat_id=chat_id)
      result = []
      for i in splitd:
        if not i.isdigit():
          continue
        i = int(i)
        re_update = utils.db.user_subscribe_list.update(status = 1 ).where(utils.User_subscribe_list.id == i,utils.User_subscribe_list.user_id == user_id)#更新状态
        re_update = re_update.execute()# 更新成功返回1，不管是否重复执行
        if re_update:
          result.append(i)
      await event.respond('success unsubscribe id:{}'.format(result if result else 'None'))
  raise events.StopPropagation

if __name__ == "__main__":

    cache.expire()

    # 开启client loop。防止进程退出
    client.run_until_disconnected()
