#coding=utf-8
"""
数据库操作类
"""
import logging,sys,os,datetime
import re
from peewee import MySQLDatabase,BigIntegerField,Model,CharField,DoubleField,IntegerField,CharField,SqliteDatabase,FloatField,SmallIntegerField,DateTimeField
from peewee import OperationalError

__all__ = [
  'db',
  'User',
  'User_subscribe_list',
  'User_block_list',
]

_current_path = os.path.dirname(os.path.realpath(__file__))

_path = '{}/.db'.format(_current_path)

# 本地 执行sqlite写入
_connect = SqliteDatabase(_path)

_connect.is_closed() and _connect.connect()

class _Base(Model):
  # #将表和数据库连接
  class Meta:
      database = _connect

class User(_Base):
  """用户数据表
  id chat_id create_time
  """
  chat_id = IntegerField(index=True,unique=True)
  create_time = DateTimeField('%Y-%m-%d %H:%M:%S',index=True)

  class Meta:
        indexes = (
          #  (('字段1', '字段2'), True),    # 字段1与字段2整体作为索引，True 代表唯一索引
          # (('字段1', '字段2'), False),   # 字段1与字段2整体作为索引，False 代表普通索引
            # (('price','type','time'), False), # 联合索引
        )

class User_subscribe_list(_Base):
  """
  用户订阅表
  user_subscribe_list
  id user_id channel_name keywords status create_time
  """
  user_id = IntegerField(index=True)
  channel_name = CharField(50,null=False)# 频道名称
  
  # https://docs.telethon.dev/en/latest/concepts/chats-vs-channels.html#channels
  chat_id = CharField(50,null=False,default='')# 频道的非官方id。 e.g. -1001630956637

  keywords = CharField(120,null=False)# 
  status = SmallIntegerField(default=0)# 0 正常 1删除
  create_time = DateTimeField('%Y-%m-%d %H:%M:%S',null=True)
  
class User_block_list(_Base):
    """
    用户屏蔽列表（黑名单设置）
    user_block_list
    id user_id blacklist_type blacklist_value channel_name chat_id  create_time update_time
    """
    user_id = IntegerField(index=True)
    
    blacklist_type = CharField(50, null=False) # 黑名单的类型。比如length_limit、keyword、username
    blacklist_value = CharField(120, null=False) # 黑名单值

    channel_name = CharField(50,null=True,default='')# 应用范围 频道名称
    chat_id = CharField(50, null=True, default='')  # 应用范围  群组/频道的非官方id。 e.g. -1001630956637，如果为空或默认值，表示所有群组
    
    create_time = DateTimeField('%Y-%m-%d %H:%M:%S', null=True)
    update_time = DateTimeField('%Y-%m-%d %H:%M:%S', null=True)

    class Meta:
        indexes = (
            # (('user_id', 'channel_name','chat_id', 'blocked_username'), True),  # user_id, chat_id和blocked_username整体作为唯一索引
        )
    
class _Db:
  def __init__(self):
    #创建实例类
    init_class = [
      User,
      User_subscribe_list,
      User_block_list,
    ]
    for model_class in init_class:
      try:
        model = model_class()
        model.table_exists() or (model.create_table()) #不存在 则创建表
        
        # 执行空查询(检测字段缺失的报错 )
        model.get_or_none(0)

        setattr(self,model_class.__name__.lower(),model)
      except OperationalError as __e:
        _e = str(__e)

        # 处理字段不存在的报错
        if 'no such column' in _e:
          find = re.search('no such column: (?:\w+\.)([a-z_0-9]+)$',_e)
          if find:
            field = find.group(1)
            if hasattr(model_class,field):
              self.add_column(model_class.__name__.lower(),getattr(model_class,field))
            else:
              raise __e

  def add_column(slef,table,field):
    '''
    动态添加字段

    https://stackoverflow.com/questions/35012012/peewee-adding-columns-on-demand

    Args:
        slef ([type]): [description]
        table ([type]): [description]
        field ([type]): [description]
    '''
    from playhouse.migrate import SqliteMigrator,migrate
    migrator = SqliteMigrator(_connect)
    migrate(
        migrator.add_column(table, field.name, field),
    )


  def __del__(self):
    # logger.debug('db connect close')
    # _connect.close()
    pass

db = _Db()
db.connect = _connect
