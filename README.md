# keyword_alert_bot
telegram keyword alert bot ⏰

用于提醒频道关键字消息

# DEMO

http://t.me/keyword_alert_bot


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