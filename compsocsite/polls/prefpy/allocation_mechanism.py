from polls.models import *
import operator
import random

# ALLOCATION ALGORITHM FUNCTIONS HERE:
def allocation(pollAlgorithm, response_set, latest_responses):
    #make sure there is at least one response  
    if len(latest_responses) == 0:
        return
    
    # allocate items to responses
    item_set = latest_responses[0].question.item_set.all()
    itemList = []
    for item in item_set:
        itemList.append(item.item_text)            

    if pollAlgorithm == 1:
        #SD early first
        allocation_serial_dictatorship(response_set, latest_responses, itemList, early_first = 1)
    elif pollAlgorithm == 2:
        #SD late first
        allocation_serial_dictatorship(list(reversed(response_set)), latest_responses, itemList, early_first = 0)
    elif pollAlgorithm == 3:
        allocation_manual(response_set, latest_responses, itemList)

# iterate through each response and assign the highest ranking choice that is still available 
# List<String> items
# List<(String, Dict<String, int>)> responses is a list of tuples, where the first entry is the user and the second
#     entry is the dictionary. Each dictionary item maps to a rank (integer) 
# return Dict<String, String> allocationResults which maps users to items
def getAllocationResults(items, responses):
    allocationResults = {}
    for response in responses:
        # no more items left to allocate
        if len(items) == 0:
            return
        
        highestRank = len(items)
        myitem = items[0]

        # here we find the item remaining that this user ranked the highest
        username = response[0]
        preferences = response[1]
        for item in items:
            if preferences.get(item) < highestRank:
                highestRank = preferences.get(item)
                myitem = item

        print ("Allocating item " + myitem + " to user " + username)
        # assign item
        allocationResults[username] = myitem
        # remove the item from consideration for other students
        items.remove(myitem)                
    return allocationResults

# update the database with the new allocation results
def assignAllocation(question, allocationResults):
    for username, item in allocationResults.items():
        currentUser = User.objects.filter(username = username)
        allocatedItem = question.item_set.get(item_text = item)
        mostRecentResponse = question.response_set.reverse().filter(user=currentUser)[0]
        mostRecentResponse.allocation = allocatedItem
        mostRecentResponse.save()
    return

# Serial dictatorship algorithm to allocate items to students for a given question.
# It takes as an argument the response set to run the algorithm on.
# The order of the serial dictatorship will be decided by increasing
# order of the timestamps on the responses for novel questions, and reverse
# order of the timestamps on the original question for follow-up questions.
def allocation_serial_dictatorship(response_set, responses, itemList, early_first = 1):
    item_set = responses[0].question.item_set.all()
    student_response_order = responses

    # it's a follow-up question, so run it in reverse order of timestamp from original question
    if responses[0].question.follow_up != None:
        response_set = []
        # in order to run the algorithm without modifying data, we query each response in this set and store a copy
        for r in student_response_order:
            response_set.append(r)

        # we set the timestamp value to be equal to timestamp of the original question and sort it in reverse order
        for r in responses:
            temp = r.question.follow_up.response_set.filter(user = r.user)[0] # this assumes the same user set responded to questions 1 and 2
            r.timestamp = temp.timestamp
        if early_first:
            response_set.sort(key = operator.attrgetter('timestamp'), reverse = True)
        else: 
            response_set.sort(key = operator.attrgetter('timestamp'), reverse = False)
        student_response_order = response_set    
            
    # allocate items to responses
    itemList = []
    for item in item_set:
        itemList.append(item.item_text)
    responseList = []
    for response in response_set:
        tempDict = {}
        for item, rank in response.dictionary_set.all()[0].items():
            tempDict[item.item_text] = rank
        responseList.append((response.user.username, tempDict))
    allocationResults = getAllocationResults(itemList, responseList)
    
    assignAllocation(responses[0].question, allocationResults)
    return

# the poll owner can specify an order to allocate choices to voters
def allocation_manual(response_set, responses, itemList):
    responseList = []
    for response in response_set:
        tempDict = {}
        for item, rank in response.dictionary_set.all()[0].items():
            tempDict[item.item_text] = rank
        responseList.append((response.user.username, tempDict))
    allocationResults = getAllocationResults(itemList, responseList)
    
    assignAllocation(responses[0].question, allocationResults)
    return