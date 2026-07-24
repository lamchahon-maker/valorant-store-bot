# 🎮 Valorant Daily Store Bot

บอทแจ้งเตือน skin ร้านค้ารายวัน Valorant ผ่าน Discord อัตโนมัติทุกวัน **07:01 น. (ไทย)**

---

## 📋 สิ่งที่ต้องมีก่อน

- Python 3.11+ บนเครื่อง PC
- Riot Games account (ที่มี Valorant)
- Discord server ที่คุณเป็น admin
- บัญชี [Railway](https://railway.app) (deploy ฟรี)
- GitHub account (สำหรับ push code)

---

## ⚡ ขั้นตอนที่ 1 — ติดตั้งและรัน Setup บนเครื่อง

```powershell
cd valorant-store-bot
pip install -r requirements.txt
python setup.py
```

หน้าจอจะถาม username, password และ 2FA code
หลังจากนั้นจะได้ RIOT_SSID ออกมา — คัดลอกเก็บไว้!

---

## ⚡ ขั้นตอนที่ 2 — สร้าง Discord Webhook

1. เปิด Discord channel ที่ต้องการรับแจ้งเตือน
2. Settings → Integrations → Webhooks → New Webhook
3. Copy Webhook URL เก็บไว้

---

## ⚡ ขั้นตอนที่ 3 — Push ขึ้น GitHub

```powershell
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/valorant-store-bot.git
git push -u origin main
```

ห้าม push ไฟล์ .env!

---

## ⚡ ขั้นตอนที่ 4 — Deploy บน Railway

1. ไปที่ railway.app → New Project → Deploy from GitHub repo
2. เลือก repo valorant-store-bot
3. ไปที่ Variables tab แล้วเพิ่ม:

| Variable | ค่า |
|----------|-----|
| RIOT_USERNAME | email Riot ของคุณ |
| RIOT_PASSWORD | password |
| RIOT_SSID | ssid cookie จาก setup.py |
| REGION | ap |
| DISCORD_WEBHOOK_URL | Webhook URL จาก Discord |

4. Railway จะ deploy อัตโนมัติ ดู logs ใน Deployments

---

## 📁 โครงสร้างไฟล์

```
valorant-store-bot/
├── auth.py          Riot authentication
├── store.py         Store API + skin info
├── notifier.py      Discord Webhook
├── main.py          Scheduler (รันบน Railway)
├── setup.py         First-time setup (รันบน PC)
├── requirements.txt
├── Procfile         Railway config
└── .env.example     ตัวอย่าง env vars
```

---

## 🔧 ssid หมดอายุ (~1 ปี)

รัน setup.py ใหม่เพื่อรับ ssid ใหม่
แล้วอัปเดต RIOT_SSID ใน Railway Variables

---

## ⏰ Schedule

Bot จะส่งแจ้งเตือนทุกวัน 07:01 น. (ไทย) = 00:01 UTC
ตรงกับเวลา reset ร้านค้าของ Valorant
