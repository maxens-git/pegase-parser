import asyncio
import json
import os
import pandas as pd
from dotenv import load_dotenv

from scraper import fetch_notes
from notifier import notify_changes

load_dotenv()

DATA_FILE = os.path.join(os.getcwd(), "last_data.json")


def load_previous_data() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_data(data: list):
    data_dict = {item['name']: item['result'] for item in data}
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=2)


def detect_changes(old_data: dict, new_data: list) -> list:
    changes = []
    for item in new_data:
        name = item['name']
        new_result = item['result']
        old_result = old_data.get(name)
        
        if old_result is None:
            if new_result != "Aucun résultat":
                changes.append({
                    'name': name,
                    'old_result': None,
                    'new_result': new_result
                })
        elif old_result != new_result:
            changes.append({
                'name': name,
                'old_result': old_result,
                'new_result': new_result
            })
    
    return changes


async def main():
    print("🔄 Récupération des notes...")
    
    data = await fetch_notes()
    
    if not data:
        print("❌ Aucune donnée récupérée")
        return
    
    df = pd.DataFrame(data)
    df.columns = ['Matière', 'Résultat']
    print("Notes et résultats:")
    print(df.to_string(index=False))
    print(f"Total: {len(df)} éléments")
    
    old_data = load_previous_data()
    
    changes = detect_changes(old_data, data)
    
    if changes:
        print(f"\n {len(changes)} changement(s) détecté(s):")
        for change in changes:
            old = change['old_result'] or 'Nouveau'
            print(f"  • {change['name']}: {old} → {change['new_result']}")
        
        notify_changes(changes)
    else:
        print("\n✅ Aucun changement détecté")
    
    save_data(data)
    print("💾 Données sauvegardées")


if __name__ == "__main__":
    asyncio.run(main())