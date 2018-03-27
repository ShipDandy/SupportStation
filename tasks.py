import re, pysftp, os, sendgrid, ssl, sqlite3, datetime
from creds import pvCreds, sgCreds
from sendgrid.helpers.mail import *


mailingList = ["joe.brower@shipstation.com", "rachel.haworth@shipstation.com"]

def baseLocation():
    return os.getcwd()

def agentQueue():
    """makes list from db and iterates through them w/ runDailyReport and calling CSV Assembler"""
    agentList = []

    connection = sqlite3.connect("zdAgents.db")
    cursor = connection.cursor()
    query = "SELECT * FROM agents"

    result = cursor.execute(query)
    result2 = result.fetchall()

    connection.close()

    for each in result2:
        agentList.append({"agentId": each[0], "agentName": each[1], "agentEmail": each[2]})

    return agentList


def zdcNameFilter(agentName):
    """Scrubs last name of agents to single letter to work with ZDC API query format"""
    reggie = re.compile(r"(.+?\s)(.).+")
    scrubbedName = reggie.sub(r'\1\2', agentName)

    return scrubbedName


def mailDamon(mailingList, statusSubject, statusBody, targetDay):
    """assembles and sends emails, iterating over list. will work out CC capabilities l8r"""

    for each in mailingList:
        sg = sendgrid.SendGridAPIClient(apikey=sgCreds["key"])
        from_email = Email("supportstation@shipstation.com")
        to_email = Email(each)
        subject = statusSubject
        content = Content("text/plain", statusBody)
        mail = Mail(from_email, subject, to_email, content)

        try:
            sg.client.mail.send.post(request_body=mail.get())
        except Exception:
            pass


def statusMailer(condition, targetDay):
    """selects email contact based on state of report"""
    statusSubject = ""
    statusBody = ""

    if condition == "uploadOk":
        statusSubject = "Success: PV Report for {} uploaded".format(targetDay)
        statusBody = "Enjoy another day of agent stats!\n\n\nI am a robot, don't try replying to this email or bees with lions for stingers will sting you!"
        mailDamon(mailingList, statusSubject, statusBody, targetDay)
    elif condition == "uploadError":
        statusSubject = "Uploading Failed for {} PV Report".format(targetDay)
        statusBody = "Retry uploading the report for {} using the SupportStation API.\n\n\nI am a robot, don't try replying to this email or bees with lions for stingers will sting you!".format(targetDay)
        mailDamon(mailingList, statusSubject, statusBody, targetDay)
    elif condition == "reportError":
        statusSubject = "Reporting Failed on PV Report for {}".format(targetDay)
        statusBody = "Retry collecting and uploading the report for {} using the SupportStation API.\n\n\nI am a robot, don't try replying to this email or bees with lions for stingers will sting you!".format(targetDay)
        mailDamon(mailingList, statusSubject, statusBody, targetDay)
    else:
        pass

def reportUploader():
    """uploads daily report, returns indication if successfuly or not"""
    uploadFile = baseLocation() + "/reporter/loadingDock/supportstation.csv"

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    sftp = pysftp.Connection(host=pvCreds["host"], username=pvCreds["username"], password=pvCreds["pass"], port=pvCreds["port"], cnopts=cnopts)

    sftp.chdir(pvCreds["folder"])

    try:
        sftp.put(uploadFile)
        sftp.close()
        return "success"
    except Exception:
        sftp.close()
        return "error"

def valiDate(targetDay):
    """checks to make sure that date passed is in expected format"""
    dateFormat = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
    
    dateCheck = dateFormat.search(targetDay)

    if dateCheck == None:
        return "Date format should be presented as YYYY-MM-DD."
    elif int(dateCheck.group(1)) > int(datetime.datetime.now().strftime("%Y")):
        return "Currently unable to pull reports from THE FUTURE."
    elif int(dateCheck.group(1)) < 2017:
        return "Please use a date from at least 2017."
    elif int(dateCheck.group(2)) > 12 or int(dateCheck.group(2)) < 1:
        return "Invalid month value, expected range between 01 - 12."
    elif int(dateCheck.group(3)) > 31 or int(dateCheck.group(3)) < 1:
        return "That's a crazy month, expected date value between 01 - 31."

    return True


