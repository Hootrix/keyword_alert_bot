#coding=utf-8
"""
数据库操作类
"""
import logging,sys,os,datetime
from peewee import MySQLDatabase,BigIntegerField,Model,CharField,DoubleField,IntegerField,CharField,SqliteDatabase,FloatField,SmallIntegerField,DateTimeField

__all__ = [
  'db',
  'User',
  'User_subscribe_list',
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
  keywords = CharField(120,null=False)# 
  status = SmallIntegerField(default=0)# 0 正常 1删除
  create_time = DateTimeField('%Y-%m-%d %H:%M:%S',null=True)
  

class _Db:
  def __init__(self):
    #创建实例类

    self.user = User()
    self.user.table_exists() or (self.user.create_table()) #不存在 则创建表
    
    self.user_subscribe_list = User_subscribe_list()
    self.user_subscribe_list.table_exists() or (self.user_subscribe_list.create_table()) #不存在 则创建表
    
    # todo
    
  def __del__(self):
    # logger.debug('db connect close')
    # _connect.close()
    pass

db = _Db()
db.connect = _connect

# bte_params = Bte_params()
# # a = bte_params.select('*').limit(1)

# a = Bte_params.select().order_by(Bte_params.id.desc()).limit(1).get()
# print(a.open_price)
