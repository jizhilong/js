# js - 健身打卡聊天机器人

## 支持的命令
### 帮助/教程类
- !js help # 显式帮助目录
- !js list # 列出所有支持的运动类型
- !js tutorial pullup # 显示一条引体向上的视频教程

### 信息查询类
- !js show # 显示我最近3天的健身记录
- !js show 10 # 显示我最近10天的健身记录
- !js show ycqian # 显示ycqian最近3天的健身记录
- !js show ycqian 7 # 显示ycqian最近7天的健身记录
- !js rank # 列出健身排行榜前十
- !js hideme # 我害羞，我想隐身，不要让其他人查到我的健身记录，也不要让我参与排行榜竞争
- !js hideme off # 关闭隐身模式

### 打卡类
- !js kbs-24 50 # 24公斤-壶铃摆荡，1组50次
- !js kbs-16 5x50 # 16公斤-壶铃摆荡，5组，每组50次
- !js kbs-12 50,40,40,40,40 # 12公斤壶铃摆荡，5组，第一组50次，之后4组各40次
- !js pullup 15 # 引体向上，1组，15次.

### 挑战类
- !js challenge list # 列出支持的挑战项目
- !js challenge kbs-10000 # 参与10000次壶铃摆荡挑战
- !js challenge show # 显示我参与的挑战项目及进度
- !js challenge recalculate # 重新计算/校准挑战进度

## 内置健身项目
### 自重类
- 引体向上
- 俯卧撑
- 双杠臂屈伸
- burpee

### 力量三大项
- 各重量颈后深蹲
- 各重量硬拉
- 各重量平板卧推

### 壶铃类
- 各重量壶铃摆荡
- 各重量壶铃深蹲
- 各重量壶铃硬拉
- 各重量壶铃实力推举
- 各重量壶铃提拉

### 弹力绳类
- 各重量弹力绳弯举
- 各重量弹力绳划船
