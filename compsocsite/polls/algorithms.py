from polls.models import Question, Item, Response, Student, Dictionary, KeyValuePair
import operator

#Algorithm to allocate items to students for a given question.
#It takes as an argument the question to run the algorithm on.
#The order of the serial dictatorship will be decided by increasing
#order of the timestamps on the responses for novel questions, and reverse
#order of the timestamps on the original question for follow-up questions.
def allocation_serial_dictatorship(responses):
	item_set = responses[0].question.item_set.all()
	student_response_order = responses

	# it's a follow-up question, so run it in reverse order of timestamp from original question
	if responses[0].question.follow_up != None:
		print "follow up question!"
		response_set = []
		for r in student_response_order:
			response_set.append(r)

		for r in responses:
			temp = r.question.follow_up.response_set.filter(student = r.student)[0] # this assumes the same student set responded to questions 1 and 2
			r.timestamp = temp.timestamp
		response_set.sort(key = operator.attrgetter('timestamp'), reverse = True)
		student_response_order = response_set
	items = []

	# this is working correctly
	for item in item_set:
		items.append(item)

	for student_response in student_response_order:
		highest_rank = len(items)
		myitem = items[0]
		prefs = student_response.dictionary_set.all()[0] # we should really change the dictionary relationship to one-to-one
		for item in items:
			if prefs.get(item) < highest_rank:
				highest_rank = prefs.get(item)
				myitem = item
		print "Allocating item " + myitem.item_text + " to student " + student_response.student.student_name
		student_response.allocation = myitem
		student_response.save()
		items.remove(myitem)
	return