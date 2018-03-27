import requests, re
from creds import zdc_headers, zd_headers
from templates.statusTemplate import dayOff
from tasks import zdcNameFilter

def getDaysChats(agentName, targetDay):
    """Use datetime date to grab day's chats and ratings, uses zdc_headers"""
    zdcAgentName = zdcNameFilter(agentName)

    chats = requests.get("https://www.zopim.com/api/v2/chats/search?q=end_timestamp:[{} TO {}] AND \"{}\"".format(targetDay, targetDay, zdcAgentName), headers=zdc_headers)

    workingInfo = dict(chats.json())

    chatCount = int(workingInfo["count"])

    goodRatingsCall = requests.get("https://www.zopim.com/api/v2/chats/search?q=end_timestamp:[{} TO {}] AND \"{}\" AND rating:good".format(targetDay, targetDay, zdcAgentName), headers=zdc_headers)

    goodRatings = dict(goodRatingsCall.json())

    badRatingsCall = requests.get("https://www.zopim.com/api/v2/chats/search?q=end_timestamp:[{} TO {}] AND \"{}\" AND rating:bad".format(targetDay, targetDay, zdcAgentName), headers=zdc_headers)

    badRatings = dict(badRatingsCall.json())

    satisfactionTally = {"good": goodRatings["count"], "bad": badRatings["count"]}

    return chatCount, satisfactionTally


def getDaysTickets(agentId, targetDay):
    """Use datetime to grab day's email based tickets and ratings, uses zd_headers"""

    tickets = requests.get("https://shipstation.zendesk.com/api/v2/search.json?query=type:ticket assignee:{} solved:{} -channel:chat".format(agentId, targetDay), headers=zd_headers)

    workingInfo = dict(tickets.json())

    emailCount = 0
    emailSatisfactionTally = []
    emailTicketList = []

    phoneInboundCount = 0
    phoneSatisfactionTally = []

    ticketTypes = ["web", "email", "api"]

    for ticket in workingInfo["results"]:
        if ticket["via"]["channel"] in ticketTypes:
            emailCount += 1
            emailSatisfactionTally.append(ticket["satisfaction_rating"]["score"])
            emailTicketList.append(ticket["url"])
        elif ticket["via"]["channel"] == "voice":
            phoneInboundCount += 1
            phoneSatisfactionTally.append(ticket["satisfaction_rating"]["score"])
        else:
            pass

    return emailCount, emailSatisfactionTally, emailTicketList, phoneInboundCount, phoneSatisfactionTally


def getDaysEmailReplies(agentId, emailTicketList):
    """Use info from getDaysEmailTickets to get day's cycle through tickets to count replies made by agentId"""
    replyCount = 0
    oneTouchCount = 0

    reggie = re.compile(r"(\d+)\.json")

    for each in emailTicketList:
        reggieBar = reggie.search(each)

        commentHistory = requests.get("https://shipstation.zendesk.com/api/v2/tickets/{}/comments.json".format(reggieBar.group(1)), headers=zd_headers)

        workingInfo = dict(commentHistory.json())
        quickCount = 0

        for comment in workingInfo["comments"]:
            if comment["type"] == ("Comment") and comment["author_id"] == int(agentId):
                quickCount += 1

        if quickCount == 1 and workingInfo["count"] == 2:
            oneTouchCount += 1

        replyCount += quickCount

    return replyCount, oneTouchCount


def getDaysSatisfaction(emailSatisfactionTally, phoneSatisfactionTally, chatRatings):
    """use info from get-phone-chat-email to count the days satisfaction ratings either good or bad. other statuses are discarded"""

    emailGood = emailSatisfactionTally.count("good")
    emailBad = emailSatisfactionTally.count("bad")

    try:
        emailSatisfaction = round(float(emailGood / (emailGood + emailBad)), 2)
    except ZeroDivisionError:
        emailSatisfaction = "NA"

    phoneGood = phoneSatisfactionTally.count("good")
    phoneBad = phoneSatisfactionTally.count("bad")

    try:
        phoneSatisfaction = round(float(phoneGood / (phoneGood + phoneBad)), 2)
    except ZeroDivisionError:
        phoneSatisfaction = "NA"

    try:
        chatSatisfaction = round(float(chatRatings["good"] / (chatRatings["good"] + chatRatings["bad"])), 2)
    except ZeroDivisionError:
        chatSatisfaction = "NA"

    return emailSatisfaction, phoneSatisfaction , chatSatisfaction


def calculateFCR(emailTicketCount, oneTouchCount):
    """takes info from getDaysEmailTickets and getDaysOneTouch to calculate first contact resolution percentage"""
    try:
        firstContactResolution = round(float(oneTouchCount / emailTicketCount), 2)
    except ZeroDivisionError:
        firstContactResolution = "NA"

    return firstContactResolution


def calculateDaysInteractions(replyCount, phoneInboundCount, chatCount, emailCount):
    """take info from getDaysReplies and getDaysChats to sum up to the day's total interactions"""
    totalInteractions = replyCount + phoneInboundCount + chatCount
    solvedInteractions = emailCount + phoneInboundCount + chatCount

    return totalInteractions, solvedInteractions

def getAgentDailyMetrics(agentId, agentName, targetDay):
    """one controller to call them all"""
    dailyMetrics = {"agentId": agentId, "agentName": agentName, "metrics": {}}

    """get chat info"""
    dailyMetrics["metrics"]["chatCount"], dailyMetrics["metrics"]["chatRatings"] = getDaysChats(agentName, targetDay)

    """get email ticket and inbound phone stats"""
    dailyMetrics["metrics"]["emailCount"], dailyMetrics["metrics"]["emailSatisfactionTally"], dailyMetrics["metrics"]["emailTicketList"], dailyMetrics["metrics"]["phoneInboundCount"], dailyMetrics["metrics"]["phoneSatisfactionTally"] = getDaysTickets(agentId, targetDay)

    if dailyMetrics["metrics"]["chatCount"] == 0 and dailyMetrics["metrics"]["emailCount"] == 0 and dailyMetrics["metrics"]["phoneInboundCount"] == 0:
        return dayOff(agentId, agentName)

    """get replies and one touch tickets"""
    dailyMetrics["metrics"]["replyCount"], dailyMetrics["metrics"]["oneTouch"] = getDaysEmailReplies(agentId, dailyMetrics["metrics"]["emailTicketList"])

    """get daily satisfaction metrics"""
    dailyMetrics["metrics"]["emailSatisfaction"], dailyMetrics["metrics"]["phoneSatisfaction"], dailyMetrics["metrics"]["chatSatisfaction"] = getDaysSatisfaction(dailyMetrics["metrics"]["emailSatisfactionTally"], dailyMetrics["metrics"]["phoneSatisfactionTally"], dailyMetrics["metrics"]["chatRatings"])

    """get first contact resolutions"""
    dailyMetrics["metrics"]["firstContact"] = calculateFCR(dailyMetrics["metrics"]["emailCount"], dailyMetrics["metrics"]["oneTouch"])

    """get total interactions for the day"""
    dailyMetrics["metrics"]["totalInteractions"], dailyMetrics["metrics"]["solvedInteractions"] = calculateDaysInteractions(dailyMetrics["metrics"]["replyCount"], dailyMetrics["metrics"]["phoneInboundCount"], dailyMetrics["metrics"]["chatCount"], dailyMetrics["metrics"]["emailCount"])

    return dailyMetrics

"""testing info"""
# day = "2018-03-03"
# agentId = "23107783388"
# agentName = "Anne O"
#
# print(getAgentDailyMetrics(agentId, agentName, day))
# print(getDaysTickets(agentId, day))
