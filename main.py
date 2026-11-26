import asyncio
import datetime

import aiohttp

from astrbot.api import logger
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register

API_BASE = "https://status.escapefromtarkov.com"

STATUS_LABEL = {
    0: "✅ 正常",
    1: "⚠️ 不稳定",
    2: "❌ 宕机/维护",
}

SERVICE_ZH = {
    "Website": "网站",
    "Forum": "论坛",
    "Authentication": "账号认证",
    "Launcher": "游戏启动器",
    "Group lobby": "组队大厅",
    "Trading": "交易市场",
    "Matchmaking": "对局匹配",
    "Friends and msg": "好友与私信",
    "Inventory operations": "仓库操作",
}


def _format_item(item: dict) -> str:
    status = item.get("status")
    label = STATUS_LABEL.get(status, f"❓ 未知状态({status})")
    name = item.get("name", "未知服务")
    zh = SERVICE_ZH.get(name)
    text = f"{name}（{zh}）" if zh else name
    region = item.get("region")
    if region:
        text += f" [{region}]"
    return f"{label} {text}"


@register("astrbot_plugin_eft_status", "Kuristina", "查询逃离塔科夫服务器状态", "1.0.0")
class EftStatusPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def _fetch(self, session: aiohttp.ClientSession, path: str):
        async with session.get(API_BASE + path) as resp:
            resp.raise_for_status()
            return await resp.json(content_type=None)

    @filter.command("塔科夫服务器", alias={"eft服务器", "eft状态", "逃离塔科夫状态"})
    async def eft_status(self, event: AstrMessageEvent):
        """查询逃离塔科夫各游戏服务器与平台服务的当前状态"""
        timeout = aiohttp.ClientTimeout(total=15)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                clock, datacenters, services, global_status = await asyncio.gather(
                    self._fetch(session, "/api/clock"),
                    self._fetch(session, "/api/datacenter/list"),
                    self._fetch(session, "/api/services"),
                    self._fetch(session, "/api/global/status"),
                )
        except Exception as e:
            logger.warning(f"查询逃离塔科夫状态失败: {e}")
            yield event.plain_result(
                "查询失败：无法访问逃离塔科夫状态官网"
                "（status.escapefromtarkov.com），可能是官网暂时不可用，请稍后再试。"
            )
            return

        msk = datetime.timezone(datetime.timedelta(hours=3))
        msk_time = datetime.datetime.fromtimestamp(clock, tz=msk)

        lines = [
            "🎮 逃离塔科夫 服务器状态",
            f"🕒 官方时间：{msk_time:%Y-%m-%d %H:%M}（MSK）",
        ]

        notice = (global_status or {}).get("message")
        if notice:
            lines.append(f"📢 官方公告：{notice}")

        lines += ["", "🖥 游戏服务器："]
        lines += [_format_item(s) for s in sorted(datacenters, key=lambda x: x.get("name", ""))]
        lines += ["", "🌐 平台服务："]
        lines += [_format_item(s) for s in services]

        all_ok = all(s.get("status") == 0 for s in datacenters) and all(
            s.get("status") == 0 for s in services
        )
        if all_ok:
            lines += ["", "🏆 所有服务器运行稳定"]

        yield event.plain_result("\n".join(lines))
