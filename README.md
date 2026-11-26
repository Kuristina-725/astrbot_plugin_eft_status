# astrbot_plugin_eft_status

查询逃离塔科夫（Escape from Tarkov）各游戏服务器与平台服务的运行状态，数据来源于官方状态页 https://status.escapefromtarkov.com/ 。

## 使用方式

在聊天中发送以下任意指令：

- `/塔科夫服务器`
- `/eft服务器`
- `/eft状态`
- `/逃离塔科夫状态`

机器人会回复各游戏服务器（亚服、欧服、俄服、非服）以及平台服务（启动器、认证、匹配、交易等）的当前状态。

## 安装

将本仓库克隆到 AstrBot 的 `data/plugins/` 目录下，然后在 WebUI 的插件页面重载即可：

```bash
cd AstrBot/data/plugins
git clone <本仓库地址> astrbot_plugin_eft_status
```

依赖：`aiohttp`（已写入 requirements.txt）。
