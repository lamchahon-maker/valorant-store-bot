"""
main.py — Entry Point
รัน scheduler ค้างไว้บน Railway และส่ง Discord notification ทุกวัน 00:00 UTC
"""

import os
import sys
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from auth import RiotAuth
from store import get_daily_store
from notifier import send_store_notification, send_error_notification

# ──────────────────────────────────────────────
# Setup
# ──────────────────────────────────────────────
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def check_env():
    """ตรวจสอบ environment variables ที่จำเป็น"""
    required = ["RIOT_USERNAME", "RIOT_PASSWORD", "RIOT_SSID", "REGION", "DISCORD_WEBHOOK_URL"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        log.error(f"❌ Missing environment variables: {', '.join(missing)}")
        log.error("กรุณาตั้งค่า env vars บน Railway ให้ครบ")
        sys.exit(1)


def run_daily_check():
    """งานหลัก: เช็ค store และส่ง Discord notification"""
    log.info("=" * 50)
    log.info("🔄 เริ่มเช็ค Valorant Daily Store...")

    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    region = os.getenv("REGION", "ap").lower()
    ssid = os.getenv("RIOT_SSID")
    username = os.getenv("RIOT_USERNAME", "")

    try:
        # ── 1. Authenticate ──────────────────────────────
        log.info("🔐 กำลัง authenticate...")
        auth = RiotAuth()

        success = auth.login_with_cookie(ssid)
        if not success:
            # Cookie หมดอายุ → ลอง login ใหม่ด้วย password
            log.warning("⚠️  ssid cookie หมดอายุ กำลัง re-login...")
            pw = os.getenv("RIOT_PASSWORD", "")
            result = auth.login(username, pw)
            if result == "multifactor":
                raise Exception(
                    "ssid cookie หมดอายุและต้องการ 2FA อีกครั้ง\n"
                    "กรุณารัน setup.py บนเครื่องของคุณเพื่อรับ ssid ใหม่ แล้วอัปเดต env var บน Railway"
                )

        log.info(f"✅ Authenticate สำเร็จ (PUUID: {auth.puuid[:8]}...)")

        # ── 2. ดึงข้อมูล Store ───────────────────────────
        log.info("🛍️  กำลังดึงข้อมูลร้านค้า...")
        skins = get_daily_store(auth, region)

        if not skins:
            raise Exception("ไม่พบข้อมูล skin ใน store")

        for s in skins:
            log.info(f"   • {s['name']} — {s['price']:,} VP")

        # ── 3. ส่ง Discord ───────────────────────────────
        log.info("📨 ส่ง Discord notification...")
        send_store_notification(webhook_url, skins, username)
        log.info("✅ เสร็จสิ้น!")

    except Exception as e:
        log.error(f"❌ Error: {e}")
        try:
            send_error_notification(webhook_url, str(e))
        except Exception:
            pass


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
if __name__ == "__main__":
    check_env()
    log.info("🚀 Valorant Store Bot เริ่มทำงาน...")
    log.info(f"   Region: {os.getenv('REGION', 'ap').upper()}")
    log.info(f"   Account: {os.getenv('RIOT_USERNAME')}")
    log.info("   Schedule: ทุกวัน 00:00 UTC (07:00 น. ไทย)")

    # รัน 1 ครั้งทันทีตอนเริ่มต้น (เพื่อทดสอบ)
    log.info("⚡ รันทดสอบครั้งแรก...")
    run_daily_check()

    # ตั้ง scheduler
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        run_daily_check,
        trigger="cron",
        hour=0,
        minute=1,  # 00:01 UTC = 07:01 น. ไทย (หลัง store reset 1 นาที)
        id="daily_store_check",
    )

    log.info("⏰ Scheduler ทำงานแล้ว — รอ 00:01 UTC ทุกวัน")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("🛑 Bot หยุดทำงาน")
