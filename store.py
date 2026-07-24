"""
store.py — Valorant Store API
ดึงข้อมูล Daily Store: skin IDs, ชื่อ, ราคา VP, รูปภาพ
"""

import requests


VALORANT_API_BASE = "https://valorant-api.com/v1"

# ──────────────────────────────────────────────
# Cache skin data เพื่อลด API calls
# ──────────────────────────────────────────────
_skin_cache: dict = {}


def get_daily_store(auth, region: str) -> list[dict]:
    """
    ดึง 4 skins ใน Daily Store

    Args:
        auth: RiotAuth instance ที่ login แล้ว
        region: เช่น 'ap', 'na', 'eu'

    Returns:
        List of skin dicts: [{name, price, image_url, tier_color}, ...]
    """
    storefront = _fetch_storefront(auth, region)
    skin_panel = storefront["SkinsPanelLayout"]

    skin_ids = skin_panel["SingleItemOffers"]
    offers = {o["OfferID"]: o for o in skin_panel["SingleItemStoreOffers"]}

    skins = []
    for skin_id in skin_ids:
        price = _get_price(offers, skin_id)
        skin_info = _get_skin_info(skin_id)
        skins.append({
            "uuid": skin_id,
            "name": skin_info.get("displayName", "Unknown Skin"),
            "price": price,
            "image_url": skin_info.get("displayIcon") or skin_info.get("fullRender", ""),
            "content_tier": skin_info.get("contentTierUuid"),
        })

    return skins


def _fetch_storefront(auth, region: str) -> dict:
    """เรียก Valorant Store API"""
    pd_url = f"https://pd.{region}.a.pvp.net"
    headers = {
        "Authorization": f"Bearer {auth.access_token}",
        "X-Riot-Entitlements-JWT": auth.entitlement_token,
        "X-Riot-ClientPlatform": (
            "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9T"
            "VmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"
        ),
        "X-Riot-ClientVersion": "release-07.12-shipping-9-889209",
    }
    resp = requests.get(
        f"{pd_url}/store/v2/storefront/{auth.puuid}",
        headers=headers,
    )
    resp.raise_for_status()
    return resp.json()


def _get_price(offers: dict, skin_id: str) -> int:
    """ดึงราคา VP ของ skin"""
    offer = offers.get(skin_id)
    if not offer:
        return 0
    costs = offer.get("Cost", {})
    # VP currency UUID
    vp_uuid = "85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"
    return costs.get(vp_uuid, 0)


def _get_skin_info(skin_level_uuid: str) -> dict:
    """ดึงข้อมูล skin จาก valorant-api.com พร้อม cache"""
    global _skin_cache

    if skin_level_uuid in _skin_cache:
        return _skin_cache[skin_level_uuid]

    try:
        resp = requests.get(
            f"{VALORANT_API_BASE}/weapons/skinlevels/{skin_level_uuid}",
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            _skin_cache[skin_level_uuid] = data
            return data
    except Exception:
        pass

    return {}


def get_tier_color(content_tier_uuid: str | None) -> int:
    """แปลง content tier เป็นสี Discord Embed (hex int)"""
    tier_colors = {
        # Select — สีทอง
        "e046854e-406c-37f4-6607-19a9ba8426fc": 0xF5A623,
        # Deluxe — สีเขียว
        "0cebb8be-46d7-c12a-d306-e9907bfc5a25": 0x5B8F3C,
        # Premium — สีฟ้าม่วง
        "60bca009-4182-7998-dee7-b8a2558dc369": 0x9B59B6,
        # Ultra — สีทองสว่าง
        "411e4a55-4e59-7757-41f0-86a53f101bb5": 0xF1C40F,
        # Exclusive — สีแดง
        "e046854e-406c-37f4-6607-19a9ba8426fc": 0xE74C3C,
    }
    return tier_colors.get(content_tier_uuid or "", 0xFF4655)  # default: Valorant red
