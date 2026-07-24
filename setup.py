"""
setup.py — รับ ssid cookie จาก browser แทนการ login ผ่าน script
วิธีนี้เลี่ยง bot detection ของ Riot ได้ 100%
"""

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from auth import RiotAuth


def main():
    print("=" * 60)
    print("  🎮  Valorant Store Bot — First-Time Setup")
    print("=" * 60)
    print()
    print("วิธีนี้ใช้ ssid cookie จาก browser ของคุณโดยตรง")
    print("ไม่ต้อง login ผ่าน script — ปลอดภัยและแม่นยำกว่า")
    print()
    print("─" * 60)
    print("📋 วิธีดึง ssid cookie:")
    print()
    print("  1. เปิด Chrome/Edge แล้วไปที่:")
    print("     https://auth.riotgames.com")
    print()
    print("  2. กด F12 เพื่อเปิด DevTools")
    print()
    print("  3. คลิก tab 'Application' (ถ้าไม่เห็น กด >> เพื่อขยาย)")
    print()
    print("  4. ด้านซ้าย: Storage → Cookies → https://auth.riotgames.com")
    print()
    print("  5. หาแถว 'ssid' แล้วคลิก 1 ครั้ง")
    print()
    print("  6. ด้านล่างจะเห็นค่า ssid (ยาวมาก) → คัดลอกทั้งหมด")
    print()
    print("─" * 60)
    print()
    print("⚠️  ถ้าไม่เห็น ssid ใน auth.riotgames.com:")
    print("   → ลองไปที่ playvalorant.com แล้ว login ก่อน")
    print("   → แล้วกลับมาเช็ค auth.riotgames.com อีกครั้ง")
    print()

    ssid = input("🍪 วาง ssid cookie ที่นี่: ").strip()

    if not ssid:
        print("❌ ไม่ได้กรอก ssid")
        sys.exit(1)

    print()
    print("🔐 กำลังทดสอบ cookie...")

    auth = RiotAuth()
    success = auth.login_with_cookie(ssid)

    if not success:
        print("❌ ssid ไม่ถูกต้องหรือหมดอายุ")
        print()
        print("แนะนำ:")
        print("  1. ไปที่ playvalorant.com → login ใหม่ก่อน")
        print("  2. แล้วดึง ssid จาก auth.riotgames.com อีกครั้ง")
        sys.exit(1)

    print(f"✅ สำเร็จ! PUUID: {auth.puuid[:8]}...")
    print()
    print("=" * 60)
    print("  นำค่าด้านล่างไปใส่ใน Railway Environment Variables")
    print("=" * 60)
    print()
    print(f"  RIOT_SSID = {ssid[:30]}...{ssid[-10:]}")
    print()
    print("(ssid เต็มๆ บันทึกไว้ใน .env แล้วถ้าตอบ y ด้านล่าง)")
    print()

    save = input("💾 บันทึก ssid ลงไฟล์ .env ด้วยไหม? (y/N): ").strip().lower()
    if save == "y":
        _update_env_file(ssid)
        print("✅ บันทึกลง .env แล้ว")

    print()
    print("📋 ขั้นตอนถัดไป:")
    print("  1. คัดลอก RIOT_SSID (ค่าเต็มๆ อยู่ใน .env)")
    print("  2. ไปที่ Railway → Project → Variables")
    print("  3. เพิ่ม RIOT_SSID = <ค่าที่คัดลอกมา>")
    print("  4. Deploy โปรเจกต์")


def _update_env_file(ssid: str):
    env_path = ".env"
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    lines = [l for l in lines if not l.startswith("RIOT_SSID=")]
    lines.append(f"RIOT_SSID={ssid}\n")
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


if __name__ == "__main__":
    main()
