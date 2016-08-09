from polls.models import *
import operator
import random

# ALLOCATION ALGORITHM FUNCTIONS HERE:
def allocation(question, allocation_order, latest_responses):
    #make sure there is at least one response  
    if len(latest_responses) == 0:
        return
    
    if question.poll_algorithm == 1:
        #SD early first
        allocation_serial_dictatorship(allocation_order, latest_responses, early_first = 1)
    elif question.poll_algorithm == 2:
        #SD late first
        allocation_serial_dictatorship(list(reversed(allocation_order)), latest_responses, early_first = 0)
    elif question.poll_algorithm == 3:
        if len(allocation_order) != 0:
            allocation_manual(allocation_order, latest_responses)
        else:
            allocation_random_assignment(latest_responses)

# if the allocation mechanism is early-first or late-first serial dictatorship, assign the order based off of latest response time
def getInitialAllocationOrder(question, latest_responses):
    if len(latest_responses) == 0:
        return

    # assign the default allocation order from earliest to latest
    counter = len(question.item_set.all())
    for user_response in (list(reversed(latest_responses))):
        # no more items left to allocate
        if counter == 0:
            return

        counter -= 1
        # create the object
        voter, created = AllocationVoter.objects.get_or_create(question=user_response.question, user=user_response.user)
        # save the most recent response
        voter.response = user_response
        voter.save()     
    return 

# get the current allocation order for this poll
# if this poll is part of a multi-poll, then it must consider the order of the previous subpolls
def getCurrentAllocationOrder(question, latest_responses):
    # get the allocation order from the first multipoll
    allocation_order = []
    if question.m_poll == True:
        multipoll = question.multipoll_set.all()[0]
        firstSubpoll = multipoll.questions.all()[0]
        allocation_order = firstSubpoll.allocationvoter_set.all()
        
        # fix the allocation order from the first subpoll
        if len(allocation_order) == 0:
            # get allocation order
            getInitialAllocationOrder(question, latest_responses)
        else:
            # copy a new allocation order based off of the first subpoll
            for alloc_item in allocation_order:
                voter, created = AllocationVoter.objects.get_or_create(question=question, user=alloc_item.user)
                voter.response = question.response_set.reverse().filter(user=alloc_item.user)[0]
                voter.save()
        allocation_order = question.allocationvoter_set.all()
    else:
        # calculate the allocation order
        allocation_order = question.allocationvoter_set.all()

        if len(allocation_order) == 0:    
            getInitialAllocationOrder(question, latest_responses)
            allocation_order = question.allocationvoter_set.all()    
    
    return allocation_order

# order user responses similar to the allocation order
def getResponseOrder(allocation_order):
    response_set = []
    for order_item in allocation_order:
        question = order_item.question
        user = order_item.user
        
        # skip if no vote
        if question.response_set.reverse().filter(user=user).count() == 0:
            continue        

        # save response
        response = question.response_set.reverse().filter(user=user)[0]
        order_item.response = response
        order_item.save()
        
        # add to the list
        response_set.append(response)
    return response_set

# iterate through each response and assign the highest ranking choice that is still available 
def assignAllocation(items, response_set):
    for user_response in response_set:
        # no more items left to allocate
        if len(items) == 0:
            return
        
        highest_rank = len(items)
        myitem = items[0]
        prefs = user_response.dictionary_set.all()[0]
        # here we find the item remaining that this user ranked the highest
        for item in items:
            if prefs.get(item) < highest_rank:
                highest_rank = prefs.get(item)
                myitem = item
        print ("Allocating item " + myitem.item_text + " to user " + user_response.user.username)
        # now we allocate that item to this user and remove that item from consideration for other students
        user_response.allocation = myitem
        user_response.save()
        items.remove(myitem)    
    return

# Serial dictatorship algorithm to allocate items to students for a given question.
# It takes as an argument the response set to run the algorithm on.
# The order of the serial dictatorship will be decided by increasing
# order of the timestamps on the responses for novel questions, and reverse
# order of the timestamps on the original question for follow-up questions.
def allocation_serial_dictatorship(allocation_order, responses, early_first = 1):
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

    # here we acquire copies of each item to use for allocation
    items = []
    for item in item_set:
        items.append(item)
        
    # get the list of responses in the specified order   
    response_set = getResponseOrder(allocation_order)
    
    # allocate items to responses
    assignAllocation(items, response_set)
    return

# the poll owner can specify an order to allocate choices to voters
def allocation_manual(allocation_order, responses):
    item_set = responses[0].question.item_set.all()
    items = []
    
    # get a list of choices
    for item in item_set:
        items.append(item)
    
    # get the list of responses in the specified order   
    response_set = getResponseOrder(allocation_order)

    # allocate items to responses
    assignAllocation(items, response_set)
    return

# This is a toy algorithm present for testing certain system functionality. It will simply allocate a random item
# to each user in the response set.
def allocation_random_assignment(responses):
    item_set = responses[0].question.item_set.all()
    student_response_order = responses
    items = []

    for item in item_set:
        items.append(item)

    for student_response in student_response_order:
        index = random.randrange(len(items))
        myitem = items[index]
        student_response.allocation = myitem
        student_response.save()
        items.remove(myitem)
    return