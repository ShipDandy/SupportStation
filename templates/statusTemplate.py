template = {
  "agentId": "",
  "agentName": "",
  "metrics": {
    "chatCount": "NA",
    "chatRatings": {
      "good": "NA",
      "bad": "NA"
    },
    "emailCount": "NA",
    "emailSatisfactionTally": [],
      "emailTicketList ": [],
      "phoneInboundCount": "NA",
      "phoneSatisfactionTally": [],
      "replyCount": "NA",
      "oneTouch": "NA",
      "emailSatisfaction": "NA",
      "phoneSatisfaction": "NA",
      "chatSatisfaction": "NA",
      "firstContact": "NA",
      "totalInteractions": "NA",
      "solvedInteractions": "NA"
    }
}

def dayOff(agentId, agentName):
    noStats = dict.copy(template)
    noStats["agentId"] = agentId
    noStats["agentName"] = agentName
    return noStats
