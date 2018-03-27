import requests, re, datetime

import creds

def chats_taken(name):
    new_chat_day = str(datetime.date.today())+"T00:00:00Z"

    name_reggie = re.compile(r'([a-zA-z]+\s[a-zA-Z])')
    assignee_name = name_reggie.search(name).group(1)

    chats_taken_raw = requests.get("https://www.zopim.com/api/v2/chats/search?q=timestamp: [" + new_chat_day + " TO *] AND \"{}\"".format(assignee_name), headers=creds.zdc_headers)
    payload =  str(chats_taken_raw.json()["count"])

    return payload

def active_chats_all():
    all_chats_raw = requests.get("https://rtm.zopim.com/stream/chats", headers=creds.zdc_headers)

    current_num = all_chats_raw.json()["content"]["data"]["active_chats"]

    payload = {"item": [{"value": current_num, "text": "Active Chats"}]}

    return payload

def get_average_wait():
    wait_raw = requests.get("https://rtm.zopim.com/stream/chats", headers=creds.zdc_headers)

    wait_num_raw = wait_raw.json()["content"]["data"]["waiting_time_avg"]

    if wait_num_raw != None:
        wait_milli = int(wait_num_raw) * 1000
        payload = {"item": [{"value": wait_milli, "text": "Average Wait Time", "type": "time_duration"}]}
        return payload
    else:
        payload = {"item": [{"value": 0, "text": "No one is waiting, Huzzah!"}]}
        return payload

def get_average_chat():
    avg_chat_raw = requests.get("https://rtm.zopim.com/stream/chats", headers=creds.zdc_headers)
    avg_chat_num_raw = avg_chat_raw.json()["content"]["data"]["chat_duration_avg"]

    if avg_chat_num_raw != None:
        chat_milli = avg_chat_num_raw * 1000
        payload = {"item": [{"value": chat_milli, "text": "Average Chat Duration", "type": "time_duration"}]}
        return payload
    else:
        payload = {"item": [{"value": 0, "text": "Not enough data."}]}
        return payload

def get_longest_wait():
    wait_raw = requests.get("https://rtm.zopim.com/stream/chats", headers=creds.zdc_headers)

    wait_num_raw = wait_raw.json()["content"]["data"]["waiting_time_max"]

    if wait_num_raw != None:
        wait_milli = int(wait_num_raw) * 1000
        payload = {"item": [{"value": wait_milli, "text": "Longest Wait Time", "type": "time_duration"}]}
        return payload
    else:
        payload = {"item": [{"value": 0, "text": "No one is waiting, Huzzah!"}]}
        return payload

def get_incoming_chats():
    incoming_raw = requests.get("https://rtm.zopim.com/stream/chats", headers=creds.zdc_headers)
    incoming_chats = incoming_raw.json()["content"]["data"]["incoming_chats"]
    payload = {"item": [{"value": incoming_chats, "text": "Incoming Chats"}]}
    return payload

def get_online_status():
    status_raw = requests.get("https://rtm.zopim.com/stream/agents", headers=creds.zdc_headers)
    agents_online = status_raw.json()["content"]["data"]["agents_online"]
    agents_away = status_raw.json()["content"]["data"]["agents_away"]
    payload = {"item": [{"text": ""},{"value": agents_away,"text": "Away"},{"value": agents_online,"text": "Online"}]}
    return payload
