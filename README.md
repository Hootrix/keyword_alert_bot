
# 🤖Telegram keyword alert bot ⏰

Telegram关键字提醒机器人，用于实时监测频道/群组中的关键字消息。

确保普通Telegram账户能够在不需要验证的情况下加入指定群组。

原理：通过Telegram命令行客户端监听消息，使用机器人向订阅用户发送消息提醒。


👉  Features：

- [x] 关键字消息订阅：根据设定的关键字和频道实时推送消息提醒
- [x] 支持正则表达式匹配语法
- [x] 支持多频道订阅 & 多关键字订阅
- [x] 支持订阅群组消息
- [x] 支持私有频道ID/邀请链接的消息订阅 

  1. https://t.me/+B8yv7lgd9FI0Y2M1  
  2. https://t.me/joinchat/B8yv7lgd9FI0Y2M1 
  

👉 Todo:

- [ ] 私有群组订阅和提醒
- [ ] 私有频道消息提醒完整内容预览
- [ ] 多账号支持
- [ ] 扫描退出无用频道/群组

# DEMO

http://t.me/keyword_alert_bot

![image](https://user-images.githubusercontent.com/10736915/171514829-4186d486-e1f4-4303-b3a9-1cfc1b571668.png)


# USAGE

## 普通关键字匹配

```
/subscribe   免费     https://t.me/tianfutong
/subscribe   优惠券   https://t.me/tianfutong

```

## 正则表达式匹配

使用类似JavaScript正则语法规则，用/包裹正则语句，目前可以使用的匹配模式：i,g

```
# 订阅手机型号关键字：iphone x，排除XR，XS等型号，且忽略大小写
/subscribe   /(iphone\s*x)(?:[^sr]|$)/ig  com9ji,xiaobaiup
/subscribe   /(iphone\s*x)(?:[^sr]|$)/ig  https://t.me/com9ji,https://t.me/xiaobaiup

# xx券
/subscribe  /([\S]{2}券)/g  https://t.me/tianfutong

```



## BUILD

### 1. config.yml.default --> config.yml

#### Create Telelgram Account & API

[开通api](https://my.telegram.org/apps) 建议使用新注册的Telegram账户

#### Create BOT 

访问https://t.me/BotFather  创建机器人

### 2. RUN

运行环境 python3.7+

首次运行需要使用Telegram账户接收数字验证码，并输入密码（Telegram API触发）。

```
$ pipenv install

$ pipenv shell

$ python3 ./main.py
```

### 3. crontab （optional）

 - update telethon

依赖库telethon可能存在旧版本不可用的情况或其他BUG，建议通过定时任务执行依赖更新。

e.g. 
```
0 0 1 * * cd /home/keyword_alert_bot && pipenv update telethon > /dev/null 2>&1
```

## BUG Q&A

 - 查看日志发现个别群组无法接收消息，而软件客户端正常接收

 请尝试更新telethon解决问题🤔，我也很无助。

 - 订阅群组消息，机器人没任何反应
 https://github.com/Hootrix/keyword_alert_bot/issues/20

 - ModuleNotFoundError: No module named 'asyncstdlib', No module named '...'

```
$ pipenv  install
```

## BOT HELP

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

Supports multiple keyword and channel subscriptions, separated by commas.

Separate keywords and channels with a space.

Main commands:

/subscribe - subscribe operation: `keyword1, keyword2 https://t.me/tianfutong,https://t.me/xiaobaiup`

/unsubscribe - unsubscribe: `keyword1, keyword2 https://t.me/tianfutong,https://t.me/xiaobaiup`

/unsubscribe_all - unsubscribe from all subscriptions

/list - display all subscription lists.
```

# License

[LICENSE](./LICENSE)


## Buy me a coffee

[USDT-TRC20]：`TDELNhqYjMJvrChjcTBiBBieWYiDGiGm2r`

<p align="center">
  <img height="260" alt="wechat pay" src="https://user-images.githubusercontent.com/10736915/231505942-533e5299-54bd-44e3-aed5-2cff2b893960.jpg" />
  <img height="260" alt="alipay" src="https://user-images.githubusercontent.com/10736915/231506223-47475d4e-3c89-4aef-ae6a-f7561c948503.jpg" />
  <a target="_blank" href="https://paypal.me/hootrix?country.x=US&locale.x=zh_XC"><img height="260" alt="paypal" src="https://user-images.githubusercontent.com/10736915/231512737-299a2074-3ce1-42b7-9230-0e34d715bca1.jpg" /></a>
  
</p>
