command_samples = [ 
    # 帮助/教程
    "!js help",                     #显式帮助目录
    "!js list ",                    #列出所有支持的运动类型
    "!js tutorial pullup ",         #显示一条引体向上的视频教程

    #信息查询类
    "!js show ",                    #显示我最近的健身记录
    "!js show ycqian ",             #显示ycqian最近的健身记录
    "!js rank ",                    #列出健身排行榜前十
    "!js hideme ",                  #我害羞，我想隐身，不要让其他人查到我的健身记录，也不要让我参与排行榜竞争

    #打卡类
    "!js kbs-24 50 ",               #24公斤-壶铃摆荡，1组50次
    "!js kbs-16 5x50 ",             #16公斤-壶铃摆荡，5组，每组50次
    "!js kbs-12 50,40,40,40,40 ",   #12公斤壶铃摆荡，5组，第一组50次，之后4组各40次
    "!js pullup 15 ",               #引体向上，1组，15次.

    #挑战类
    "!js challenge list ",          #列出支持的挑战项目
    "!js challenge kbs-10000 ",     #参与10000次壶铃摆荡挑战
    "!js challenge show ",          #显式我参与的挑战项目及进度
]


beary_request_sample = {
  "token" : "robot_token",
  "ts" : 1355517523,
  "text" : "!js help",
  "trigger_word" : "!js",
  "subdomain" : "your_domain",
  "channel_name" : "your_channel",
  "user_name" : "your_name"
}