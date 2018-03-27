import os, sys, re
from templates.statusTemplate import dayOff
from tasks import baseLocation
from reporter.reporting import getAgentDailyMetrics

def runAgentDailyReport(agentId, agentName, agentEmail, targetDay):
    """calls reporting module to collect information for a single agent"""
    dailyInfo = getAgentDailyMetrics(agentId, agentName, targetDay)

    timestamp = targetDay + "T07:00:00Z"

    infoString = str('"{}",{},{},{},{},{},{},{},{},{},{},{},"{}"'.format(agentEmail, dailyInfo["metrics"]["totalInteractions"], dailyInfo["metrics"]["solvedInteractions"], dailyInfo["metrics"]["firstContact"], dailyInfo["metrics"]["chatSatisfaction"], dailyInfo["metrics"]["phoneSatisfaction"], dailyInfo["metrics"]["emailSatisfaction"], dailyInfo["metrics"]["phoneInboundCount"], dailyInfo["metrics"]["emailCount"], dailyInfo["metrics"]["chatCount"], dailyInfo["metrics"]["oneTouch"], dailyInfo["metrics"]["replyCount"], timestamp))

    nullValues = re.compile(r"NA")

    return ("\n" + nullValues.sub("", infoString))

def makeDailyCsv():
    """copies from template and reports CSV in proper directory, requires OS module"""

    if os.path.isfile(baseLocation() + "/reporter/loadingDock/supportstation.csv"):
        os.unlink(baseLocation() + "/reporter/loadingDock/supportstation.csv")

    templateFile = open(baseLocation() + "/templates/supportstation.csv", "r")
    templateInfo = templateFile.read()
    templateFile.close()

    dailyCsv = open(baseLocation() + "/reporter/loadingDock/supportstation.csv", "w", encoding="UTF-8")
    dailyCsv.write(templateInfo)
    dailyCsv.close()


def csvArchiver(writeString, targetDay):
    """makes a backup file or upload in case of issues with upload on a certain day"""

    if os.path.isfile(baseLocation() + "/reporter/crypt/report_{}.csv".format(targetDay)):
        os.unlink(baseLocation() + "/reporter/crypt/report_{}.csv".format(targetDay))

    templateFile = open(baseLocation() + "/templates/supportstation.csv", "r")
    templateInfo = templateFile.read()
    templateFile.close()

    backupCSV = open(baseLocation() + "/reporter/crypt/report_{}.csv".format(targetDay), "w", encoding="UTF-8")
    backupCSV.write(templateInfo + writeString)
    backupCSV.close()

def csvWriter(writeQueue, targetDay):
    """takes agent queue from agentQueue and calls runAgentDailyReport for each in queue. Have try logic, collect all info then open and write to file once."""

    writeString = ""

    for each in writeQueue:
        try:
            writeString += runAgentDailyReport(each["agentId"], each["agentName"], each["agentEmail"], targetDay)
        except Exception:
            writeString += "\nError handling " + each["agentName"] + ",,,,,,,,,,,,"

    makeDailyCsv()

    dailyWrite = open(baseLocation() + "/reporter/loadingDock/supportstation.csv", "a", encoding="UTF-8")
    dailyWrite.write(writeString)
    dailyWrite.close

    csvArchiver(writeString, targetDay)

    return "Daily Report Written"



