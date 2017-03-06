from polls.models import *
from appauth.models import *
import xml.etree.ElementTree as ET
import requests


def callbackfunction(tree):
	url = "http://rpidirectory.appspot.com/api?q=" + tree[0][0].text.lower() + "&token=rcsid"
	r = requests.get(url)

	print(ET.tostring(tree))
	username = tree[0][0].text.lower() + "@rpi.edu"
	tree[0][0].text = username
	user, user_created = User.objects.get_or_create(username=username)
	# if(user.first_name = ''):
	# 	print("hi!")
	# 	user.first_name = r.json()['data'][0]['first_name']
	# 	user.last_name = r.json()['data'][0]['last_name']
	# 	user.save()
	if(user_created):
		profile = UserProfile(user = user, displayPref = 1)
		profile.save()
		user.first_name = r.json()['data'][0]['first_name'].title()
		user.last_name = r.json()['data'][0]['last_name'].title()
		user.email = username
		user.is_active = True
		user.save()