"""
notifier.py — Discord Webhook Notifier
ส่งข้อมูล Daily Store ไปยัง Discord ในรูปแบบ Embed สวยงาม
"""

import requests
from datetime import datetime, timezone, timedelta
from store import get_tier_color


TH_TZ = timezone(timedelta(hours=7))


def send_store_notification(webhook_url: str, skins: list[dict], username: str = ""):
    """
    ส่ง Discord Embed พร้อมข้อมูล Daily Store

    Args:
        webhook_url: Discord Webhook URL
        skins: list จาก store.get_daily_store()
        username: ชื่อ Riot account (optional, แสดงใน footer)
    """
    now_th = datetime.now(TH_TZ)
    date_str = now_th.strftime("%d %B %Y")

    # สร้าง embeds หนึ่งอันต่อ skin
    embeds = []

    # Header embed
    embeds.append({
        "title": "🛍️  Valorant Daily Store",
        "description": f"📅 **{date_str}**\nร้านค้าจะ reset ใน 24 ชั่วโมง",
        "color": 0xFF4655,  # Valorant Red
        "thumbnail": {
            "url": "https://media.valorant-api.com/sprays/290565e7-36b4-b776-0d3f-a6852b1d7570/displayicon.png"
        },
    })

    # Skin embeds
    for i, skin in enumerate(skins, 1):
        price_str = f"**{skin['price']:,} VP**" if skin["price"] > 0 else "ไม่ทราบราคา"
        color = get_tier_color(skin.get("content_tier"))

        embed = {
            "title": f"{skin['name']}",
            "description": f"💎 ราคา: {price_str}",
            "color": color,
        }

        # เพิ่มรูปภาพถ้ามี
        if skin.get("image_url"):
            embed["image"] = {"url": skin["image_url"]}

        embeds.append(embed)

    # Footer embed (summary)
    total_vp = sum(s["price"] for s in skins)
    skin_names = "\n".join(f"• {s['name']} — {s['price']:,} VP" for s in skins)
    embeds.append({
        "description": f"**สรุป**\n{skin_names}\n\n💰 รวมทั้งหมด: **{total_vp:,} VP**",
        "color": 0x2C2F33,
        "footer": {
            "text": f"Account: {username}  •  Valorant Store Bot",
            "icon_url": "https://media.valorant-api.com/sprays/290565e7-36b4-b776-0d3f-a6852b1d7570/displayicon.png",
        },
    })

    payload = {
        "username": "Valorant Store",
        "avatar_url": "https://media.valorant-api.com/sprays/290565e7-36b4-b776-0d3f-a6852b1d7570/displayicon.png",
        "embeds": embeds,
    }

    resp = requests.post(webhook_url, json=payload)

    if resp.status_code not in (200, 204):
        raise Exception(f"Discord webhook error {resp.status_code}: {resp.text}")

    print(f"✅ ส่ง Discord notification สำเร็จ ({len(skins)} skins)")


def send_error_notification(webhook_url: str, error_msg: str):
    """ส่ง error notification ไปยัง Discord"""
    payload = {
        "username": "Valorant Store",
        "embeds": [{
            "title": "❌ Store Bot Error",
            "description": f"```{error_msg}```",
            "color": 0xFF0000,
            "footer": {"text": "กรุณาตรวจสอบ logs บน Railway"},
        }],
    }
    requests.post(webhook_url, json=payload)
