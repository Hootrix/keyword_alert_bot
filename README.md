# keyword_alert_bot
telegram keyword alert bot ⏰

用于提醒 频道/群组 关键字消息

如果想订阅`群组`消息，确保默认账户可以不用验证的加入该群组

# DEMO

http://t.me/keyword_alert_bot

# USAGE EXAMPLE

```
# 正则
# 使用js正则语法规则，用/包裹正则语句，目前可以使用的匹配模式：i,g

# 订阅手机型号关键字：iphone x，排除XR，XS等型号，且忽略大小写
/subscribe   /(iphone\s*x)(?:[^sr]|$)/ig  https://t.me/com9ji,https://t.me/xiaobaiup

# xx券
/subscribe  /([\S]{2}券)/g  https://t.me/tianfutong

---

# 普通关键字

# 订阅关键字：免费
/subscribe   免费    https://t.me/tianfutong

```


## BUILD

1. 修改config中的配置
需要给tg账户开通api，创建一个新的bot

2. 创建运行环境运行

```
pipenv install

pipenv shell

python3 main.py
```

## bot command

```

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
```