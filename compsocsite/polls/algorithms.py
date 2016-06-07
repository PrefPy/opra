from polls.models import Question, Item, Response, Student, Dictionary, KeyValuePair
import operator
import random

# ALLOCATION ALGORITHM FUNCTIONS HERE:

# Serial dictatorship algorithm to allocate items to students for a given question.
# It takes as an argument the response set to run the algorithm on.
# The order of the serial dictatorship will be decided by increasing
# order of the timestamps on the responses for novel questions, and reverse
# order of the timestamps on the original question for follow-up questions.
def allocation_serial_dictatorship(responses):
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
			temp = r.question.follow_up.response_set.filter(student = r.student)[0] # this assumes the same student set responded to questions 1 and 2
			r.timestamp = temp.timestamp
		response_set.sort(key = operator.attrgetter('timestamp'), reverse = True)
		student_response_order = response_set
	items = []
	# here we acquire copies of each item to use for allocation
	for item in item_set:
		items.append(item)

	# the ordering of students is already set, so this loop only needs to do the allocation one by one
	for student_response in student_response_order:
		highest_rank = len(items)
		myitem = items[0]
		prefs = student_response.dictionary_set.all()[0]
		# here we find the item remaining that this student ranked the highest
		for item in items:
			if prefs.get(item) < highest_rank:
				highest_rank = prefs.get(item)
				myitem = item
		print ("Allocating item " + myitem.item_text + " to student " + student_response.student.student_name)
		# now we allocate that item to this student and remove that item from consideration for other students
		student_response.allocation = myitem
		student_response.save()
		items.remove(myitem)
	return

# This is a toy algorithm present for testing certain system functionality. It will simply allocate a random item
# to each student in the response set.
def allocation_random_assignment(responses):
	item_set = responses[0].question.item_set.all()
	student_response_order = responses
	items = []

	for item in item_set:
		items.append(item)

	for student_response in student_response_order:
		index = random.randrange(items.len())
		myitem = items[index]
		student_response.allocation = myitem
		student_response.save()
		items.remove(myitem)
	return