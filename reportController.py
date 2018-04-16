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
    """run scheduled report, to accommodate for ZenDesk's time delay to case completion we are going to query for the previous day."""
    # todayTheDayToday = str(datetime.datetime.now(tz=pytz.timezone("US/Central")).date())
    yesterdayTheDay = str((datetime.datetime.now(tz=pytz.timezone("US/Central")) - datetime.timedelta(days=1)).date())
    try:
        runDailyReport(yesterdayTheDay)
    except Exception:
        return "log it"
