import os
import requests
from dotenv import load_dotenv

load_dotenv()


def send_notification(title: str, message: str, priority: str = "default"):
    ntfy_topic = os.getenv("NTFY_TOPIC")
    ntfy_server = os.getenv("NTFY_SERVER", "https://ntfy.sh")
    ntfy_token = os.getenv("NTFY_TOKEN")
    
    if not ntfy_topic:
        print("NTFY_TOPIC non configuré")
        return False
    
    url = f"{ntfy_server}"
    
    # Utiliser l'API JSON pour supporter les caractères UTF-8/emojis
    payload = {
        "topic": ntfy_topic,
        "title": title,
        "message": message,
        "priority": 4 if priority == "high" else 3,
        "tags": ["school", "mortar_board"]
    }
    
    headers = {"Content-Type": "application/json"}
    
    if ntfy_token:
        headers["Authorization"] = f"Bearer {ntfy_token}"
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"✅ Notification envoyée: {title}")
        return True
    except requests.RequestException as e:
        print(f"❌ Erreur envoi notification: {e}")
        return False


def notify_changes(changes: list):
    if not changes:
        return
    
    title = f"📝 {len(changes)} note(s) mise(s) à jour"
    
    lines = []
    for change in changes:
        name = change['name']
        old = change.get('old_result')
        new = change['new_result']
        
        if old is None or old == "Aucun résultat":
            lines.append(f"🆕 {name}\n   → {new}")
        else:
            lines.append(f"✏️ {name}\n   {old} → {new}")
    
    message = "\n".join(lines)
    
    send_notification(title, message, priority="high")
