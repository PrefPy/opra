from polls.models import Question, Item, Response, Student, Dictionary, KeyValuePair

item_set = Item.objects.all()[:5]
student_order = Response.objects.filter(question__question_text = item_set[0].question.question_text)
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

