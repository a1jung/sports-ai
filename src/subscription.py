# src/subscription.py
# Simple local subscription mock (subscriptions.json)
import json
import os
from typing import Dict

SUB_FILE = os.path.abspath('subscriptions.json')

def load_subscriptions() -> Dict:
    if os.path.exists(SUB_FILE):
        try:
            with open(SUB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_subscriptions(data: Dict):
    with open(SUB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_subscription(user_id: str, monthly_krw: int = 1000) -> Dict:
    subs = load_subscriptions()
    subs[user_id] = {'status':'active','monthly_krw':monthly_krw}
    save_subscriptions(subs)
    return subs[user_id]

def cancel_subscription(user_id: str) -> bool:
    subs = load_subscriptions()
    if user_id in subs:
        subs[user_id]['status'] = 'canceled'
        save_subscriptions(subs)
        return True
    return False

def check_subscription(user_id: str) -> bool:
    subs = load_subscriptions()
    info = subs.get(user_id)
    return bool(info and info.get('status') == 'active')
