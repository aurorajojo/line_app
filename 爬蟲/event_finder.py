# event_finder.py

import subprocess
import json

def get_latest_events(path="artssalon_events.json"):
    result = subprocess.run(["python", "find_Event_In_Arts_Salon.py"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"爬蟲錯誤：{result.stderr}")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
