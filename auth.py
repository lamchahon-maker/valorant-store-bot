"""
auth.py — Riot Games Authentication
ใช้ ssid cookie ที่ดึงจาก browser โดยตรง (ไม่ต้อง login ผ่าน script)
"""

import re
import requests


class RiotAuth:
    ENTITLEMENT_URL = "https://entitlements.auth.riotgames.com/api/token/v1"
    USERINFO_URL = "https://auth.riotgames.com/userinfo"
    AUTH_URL = "https://auth.riotgames.com/api/v1/authorization"

    AUTH_PAYLOAD = {
        "client_id": "play-valorant-web-prod",
        "nonce": "1",
        "redirect_uri": "https://playvalorant.com/opt_in",
        "response_type": "token id_token",
        "scope": "account openid",
    }

    HEADERS = {
        "User-Agent": "RiotClient/63.0.9.4789974.4789974 rso-auth (Windows;10;;Professional, x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json, text/plain, */*",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.access_token = None
        self.entitlement_token = None
        self.puuid = None

    def login_with_cookie(self, ssid: str) -> bool:
        """
        Authenticate โดยใช้ ssid cookie ที่ดึงจาก browser
        Returns: True ถ้าสำเร็จ, False ถ้า cookie หมดอายุ
        """
        self.session.cookies.set("ssid", ssid, domain="auth.riotgames.com")

        resp = self.session.post(self.AUTH_URL, json=self.AUTH_PAYLOAD)
        data = resp.json()

        if data.get("type") == "response":
            self._handle_response(data)
            return True
        else:
            print(f"   [debug] cookie auth response: {data.get('type')} / {data.get('error', '')}")
            return False

    def get_ssid(self) -> str | None:
        """ดึง ssid cookie"""
        return self.session.cookies.get("ssid")

    def _handle_response(self, data: dict):
        uri = data["response"]["parameters"]["uri"]
        self.access_token = self._parse_token_from_uri(uri)
        self._fetch_entitlement()
        self._fetch_userinfo()

    def _parse_token_from_uri(self, uri: str) -> str:
        match = re.search(r"access_token=([^&]+)", uri)
        if not match:
            raise Exception(f"ไม่พบ access_token ใน URI: {uri}")
        return match.group(1)

    def _fetch_entitlement(self):
        resp = self.session.post(
            self.ENTITLEMENT_URL,
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={},
        )
        self.entitlement_token = resp.json()["entitlements_token"]

    def _fetch_userinfo(self):
        resp = self.session.get(
            self.USERINFO_URL,
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        self.puuid = resp.json()["sub"]
