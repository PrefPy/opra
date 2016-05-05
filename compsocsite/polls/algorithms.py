from polls.models import Question, Item, Response, Student, Dictionary, KeyValuePair
import operator

#Algorithm to allocate items to students for a given question.
#It takes as an argument the question to run the algorithm on.
#The order of the serial dictatorship will be decided by increasing
#order of the timestamps on the responses for novel questions, and reverse
#order of the timestamps on the original question for follow-up questions.
def allocation_serial_dictatorship(responses):
	item_set = responses[0].question.item_set.all()
	student_order = responses
	if responses[0].question.follow_up != None:
		response_set = []
		for r in student_order:
			response_set.append(r)

		for r in responses:
			temp = r.question.follow_up.response_set.filter(student = r.student)
			r.timestamp = temp.timestamp
		response_set.sort(key = operator.attrgetter('timestamp'), reverse = True)
		student_order = response_set
	items = []

	for item in item_set:
		items.append(item)

	for student in student_order:
		highest_rank = items.len()
		prefs = student.dictionary_set.all()[0]
		for item in items:
			if prefs.get(item) < highest_rank:
				highest_rank = prefs.get(item)
				myitem = item
		print "Allocating item " + myitem.item_text + " to student " + student.student.student_name
		student.update(allocation = myitem)
		items.remove(myitem)
	return