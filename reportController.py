import datetime, time, pytz, os, sys
from reporter.reportCompiler import csvWriter
from tasks import reportUploader, statusMailer, agentQueue
# from reporter.reporting import getAgentDailyMetrics


def processReport(targetDay):
    """run report for target day, will need to give file a special date oriented"""
    agentList = agentQueue()
    try:
        csvWriter(agentList, targetDay)
        return "success"
    except Exception:
        return "report error"
    return csvWriter(agentList, targetDay)


def runDailyReport(targetDay):
    """run report on specific day and have it archived and uploaded"""

    report = processReport(targetDay)

    if report == "success":
        upload = reportUploader()
        if upload == "success":
            statusMailer("uploadOk", targetDay)
        else:
            statusMailer("uploadError", targetDay)
    else:
        statusMailer("reportError", targetDay)


def scheduledDailyReport():
    """run report for current day"""
    todayTheDayToday = str(datetime.datetime.now(tz=pytz.timezone("US/Central")).date())
    try:
        runDailyReport(todayTheDayToday)
    except Exception:
        return "log it"
