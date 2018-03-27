"""
SupportStation: Agent Metric Reporting Tool
Author: Zeke (Joe) Brower
Version 0.99
2018-03-27
"""
from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
import requests, re, datetime, threading

from semiOpenApi import agents, tickets, chats
from reportController import runDailyReport, scheduledDailyReport
from tasks import valiDate

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify("Get Outta Here Would Ya!")

@app.route("/agents")
def list_agents():
    return jsonify(agents.list_agents_in_db())

@app.route("/agents/build_db")
def build_db():
    pass

@app.route("/agents/add_agent", methods=["POST"])
def add_agent():
    data = request.get_json()
    agent_spec = (data["zd_id"], data["agentName"], data["agentEmail"])
    return jsonify(agents.add_agent_to_db(agent_spec))

@app.route("/agents/delete_agent", methods=["DELETE"])
def delete_agent():
    data = request.get_json()
    return jsonify(agents.delete_agent_from_db(data["zd_id"]))

@app.route("/agents/update_name", methods=["PUT"])
def update_name():
    data = request.get_json()
    return jsonify(agents.update_agent_name(data["newName"], data["zd_id"]))

@app.route("/metrics/<string:name>")
def get_agent_metrics(name):
    siftName = name.replace("_", " ")
    try:
        zd_id = agents.get_agent_id(siftName)
    except TypeError:
        return jsonify({"message": "Name not found in database. Check that the name is spelled as appears in DB or that agent is present in DB."}), 404

    both_tickets = tickets.agent_tickets(zd_id)
    open_tickets = both_tickets[0]
    solved_tickets = both_tickets[1]
    days_chats = chats.chats_taken(siftName)

    current_metrics = [
    {
    "title": {"text": "Chats Taken: " + days_chats}
    },
    {
    "title": {"text": "Tickets in OPEN: " + open_tickets}
    },
    {
    "title": {"text": "Tickets in SOLVED: " + solved_tickets}
    }
    ]

    return jsonify(current_metrics)

### Chat Info ###

@app.route("/chats/active_chats")
def active_chats():
    return jsonify(chats.active_chats_all())

@app.route("/chats/average_wait")
def average_wait_time():
    return jsonify(chats.get_average_wait())

@app.route("/chats/average_chat")
def average_chat_time():
    return jsonify(chats.get_average_chat())

@app.route("/chats/longest_wait")
def longest_wait_time():
    return jsonify(chats.get_longest_wait())

@app.route("/chats/incoming_chats")
def incoming_chats():
    return jsonify(chats.get_incoming_chats())

@app.route("/chats/online_status")
def online_status():
    return jsonify(chats.get_online_status())

"""CSV Reporter Section"""

@app.route("/csv/manual_report", methods=["POST"])
def manualReport():
    data = request.get_json()
    requestDate = valiDate(data["date"])

    if requestDate != True:
        return jsonify({"errorMessage": requestDate}), 400

    csvThread = threading.Thread(target=runDailyReport, args=(data["date"],))
    csvThread.start()

    return jsonify({"message": "Report generating, check email for result status"}), 202

def runscheduledDailyReport():
    dailyThread = threading.Thread(target=scheduledDailyReport)
    dailyThread.start()


"""Scheduler"""

dailySchedule = BackgroundScheduler()
dailySchedule.add_job(runscheduledDailyReport, "cron", hour=22, timezone="US/Central")
dailySchedule.start()

if __name__ == "__main__":
    app.run()

# app.run(port=5000, debug=True, use_reloader=False)
