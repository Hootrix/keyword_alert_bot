
# 🤖Telegram keyword alert bot ⏰


用于提醒 频道/群组 关键字消息

如果想订阅`群组`消息，确保普通TG账户加入该群组不需要验证。

原理：tg命令行客户端来监听消息，使用bot来发送消息给订阅用户。

👉  Features：

- 关键字消息订阅：根据设定的关键字和频道来发送新消息提醒
- 支持正则表达式匹配语法
- 支持多频道订阅 & 多关键字订阅
- 支持订阅群组消息

# DEMO

http://t.me/keyword_alert_bot

# USAGE

```
# 正则
# 使用js正则语法规则，用/包裹正则语句，目前可以使用的匹配模式：i,g

# 订阅手机型号关键字：iphone x，排除XR，XS等型号，且忽略大小写
/subscribe   /(iphone\s*x)(?:[^sr]|$)/ig  com9ji,xiaobaiup

/subscribe   /(iphone\s*x)(?:[^sr]|$)/ig  https://t.me/com9ji,https://t.me/xiaobaiup

# xx券
/subscribe  /([\S]{2}券)/g  https://t.me/tianfutong

---

# 普通关键字

# 订阅关键字：免费
/subscribe   免费    https://t.me/tianfutong

```

## 给小白看的安装过程

https://my.telegram.org/apps 获得
```
api_id
api_hash
```

@botfather /newbot 获得
```
bot_token
bot_name
```

依次执行命令
```
cd /etc/
wget https://github.com/Hootrix/keyword_alert_bot/archive/refs/heads/master.zip
unzip master.zip
cd keyword_alert_bot-master/

nano config.yml.default
mv config.yml.default config.yml

apt update
apt install -y pip screen
pip3 install telethon peewee PySocks diskcache PyYAML

screen -S tgbot
python3 /etc/keyword_alert_bot-master/main.py

crontab -e
@reboot ( sleep 90 ; python3 /etc/keyword_alert_bot-master/main.py )
```

## BUG Q&A

 - 查看日志发现个别群组无法接收消息，软件客户端正常接收
 
 请尝试更新telethon解决问题🤔，我也很无助。

## bot help

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
