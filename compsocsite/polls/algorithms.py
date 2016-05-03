from polls.models import Question, Item, Response, Student, Dictionary, KeyValuePair
import operator

def allocation_serial_dictatorship(the_question):
	item_set = Item.objects.filter(question = the_question)
	student_order = Response.objects.filter(question = the_question)
	if the_question.follow_up != None:
		responses = []
		for r in student_order:
			responses.append(r)

		for r in responses:
			temp = r.question.follow_up.response_set.filter(student = r.student)
			r.timestamp = temp.timestamp
		responses.sort(key = operator.attrgetter('timestamp'), reverse = True)
		student_order = responses
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
		student.allocation = myitem
		student.save()
		items.remove(myitem)
	return