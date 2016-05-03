from polls.models import Question, Item, Response, Student, Dictionary, KeyValuePair

def allocation_serial_dictatorship(the_question):
	item_set = Item.objects.filter(question = the_question)
	student_order = Response.objects.filter(question__question_text = the_question.question_text)
	items = []

	for item in item_set:
		items.append(item)

	for student in student_order:
		highest_rank = -1
		prefs = student.dictionary_set.all()[0]
		for item in items:
			if prefs.get(item) > highest_rank:
				highest_rank = prefs.get(item)
				myitem = item
		print "Allocating item " + myitem.item_text + " to student " + student.student.student_name
		student.allocation = myitem
		student.save()
		items.remove(myitem)
