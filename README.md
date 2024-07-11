
# 🤖Telegram keyword alert bot⏰

![Build Status](https://github.com/Hootrix/keyword_alert_bot/workflows/CI/CD%20Pipeline/badge.svg)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/github/license/Hootrix/keyword_alert_bot)](https://github.com/Hootrix/keyword_alert_bot/blob/master/LICENSE)
[![Paypal Donate](https://img.shields.io/badge/Paypal%20Donate-yellow?style=flat&logo=paypal)](https://www.paypal.com/donate/?business=DRVVDHMVL8G7Q&no_recurring=0&item_name=Sponsored+development+of+keyword_alert_bot%21+&currency_code=USD)
[![Github Sponsor](https://img.shields.io/badge/Github%20Sponsor-yellow?style=flat&logo=github)](https://github.com/sponsors/Hootrix)

Telegram关键字提醒机器人，用于实时监测频道/群组中的关键字消息。

确保普通Telegram账户能够在不需要验证的情况下加入指定群组。

Warning: Demo bot使用过载，建议使用 Docker 镜像自行搭建。


👉  Features：

- [x] 关键字消息订阅：根据设定的关键字和频道实时推送消息提醒
- [x] 支持正则表达式匹配语法
- [x] 支持多频道订阅 & 多关键字订阅
- [x] 支持订阅群组消息
- [x] 支持私有频道ID/邀请链接的消息订阅 

  1. https://t.me/+B8yv7lgd9FI0Y2M1  
  2. https://t.me/joinchat/B8yv7lgd9FI0Y2M1 
  

👉 Todo:

- [x] 私有群组订阅和提醒
- [ ] 私有频道消息提醒完整内容预览
- [ ] 多账号支持
- [ ] 扫描退出无用频道/群组

## 🔍Demo

http://t.me/keyword_alert_bot

<img width="250px" alt="demo" src="https://user-images.githubusercontent.com/10736915/171514829-4186d486-e1f4-4303-b3a9-1cfc1b571668.png" />


## 🚀Run

### 1. 配置文件

#### config.yml.default --> config.yml

将 config.yml.default 复制到本地并重命名为 config.yml，然后根据下面申请的 api 进行配置

#### Create Telelgram Account & API

建议使用新Telegram账户[开通api](https://my.telegram.org/apps) 来使用

#### Create BOT 

https://t.me/BotFather  创建机器人


### 2. 🐳Docker

配置好config.yml文件后，使用docker命令一键启动
```
$ docker run -it --name keyword_alert_bot -v $(pwd)/config.yml:/app/config.yml   yha8897/keyword_alert_bot



Please enter the code you received: 12345
Please enter your password: 
Signed in successfully as DEMO; remember to not break the ToS or you will risk an account ban!

#################################################################
##                                                             ##
##                          ● success                          ##
##   🤖️Telegram keyword alert bot (Version: 20240627.f6672cf)  ##
##                                                             ##
#################################################################

```

首次运行需要Telegram账户接收数字验证码，并输入密码（Telegram API触发），之后提示success即成功启动

之后可以直接根据容器名重启或者停止：

```
$ docker restart keyword_alert_bot
$ docker stop keyword_alert_bot
```


## 💪Manual Build

运行环境 python3.7+


```
$ pipenv install

$ pipenv shell

$ python3 ./main.py
```

### crontab （optional）

 - update telethon

依赖库telethon可能存在旧版本不可用的情况或其他BUG，建议通过定时任务执行依赖更新。

e.g. 
```
0 0 * * * cd /PATH/keyword_alert_bot && pipenv  telethon > /dev/null 2>&1
```

## 📘Usage

### 普通关键字匹配

```
/subscribe   免费     https://t.me/tianfutong
/subscribe   优惠券   https://t.me/tianfutong

```

### 正则表达式匹配

使用类似JavaScript正则语法规则，用/包裹正则语句，目前可以使用的匹配模式：i,g

```
# 订阅手机型号关键字：iphone x，排除XR，XS等型号，且忽略大小写
/subscribe   /(iphone\s*x)(?:[^sr]|$)/ig  com9ji,xiaobaiup
/subscribe   /(iphone\s*x)(?:[^sr]|$)/ig  https://t.me/com9ji,https://t.me/xiaobaiup

# xx券
/subscribe  /([\S]{2}券)/g  https://t.me/tianfutong

```



## Q & A

> Bug Feedback: https://github.com/Hootrix/keyword_alert_bot/issues


 ### 1. You have joined too many channels/supergroups (caused by JoinChannelRequest)

 BOT中所有订阅频道的总数超过 500。原因是BOT使用的Telegram演示账户限制导致。建议你自行部署

 ### 2. 查看日志发现个别群组无法接收消息，而软件客户端正常接收

 🤔尝试更新telethon到最新版本或者稳定的1.24.0版本

 ### 3. 订阅群组消息，机器人没任何反应
 https://github.com/Hootrix/keyword_alert_bot/issues/20

 ### 4. ModuleNotFoundError: No module named 'asyncstdlib', No module named '...'

```
$ pipenv  install
```

 ### 5. 同时存在多关键字如何匹配

```
/(?=.*cc)(?=.*bb)(?=.*aa).*/
```


## ☕ Buy me a coffee

[USDT-TRC20]：`TDELNhqYjMJvrChjcTBiBBieWYiDGiGm2r`

<p align="center">
  <img height="260" alt="wechat pay" src="https://user-images.githubusercontent.com/10736915/231505942-533e5299-54bd-44e3-aed5-2cff2b893960.jpg" />
  <img height="260" alt="alipay" src="https://user-images.githubusercontent.com/10736915/231506223-47475d4e-3c89-4aef-ae6a-f7561c948503.jpg" />
  <a target="_blank" href="https://paypal.me/hootrix?country.x=US&locale.x=zh_XC"><img height="260" alt="paypal" src="https://user-images.githubusercontent.com/10736915/231512737-299a2074-3ce1-42b7-9230-0e34d715bca1.jpg" /></a>
  
</p>
