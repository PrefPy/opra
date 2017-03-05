from polls.models import *
from appauth.models import *
import xml.etree.ElementTree as ET

def callbackfunction(tree):
	print(ET.tostring(tree))
	username = tree[0][0].text.lower() + "@rpi.edu"
	tree[0][0].text = username
	user, user_created = User.objects.get_or_create(username=username)
	if(user_created):
		profile = UserProfile(user = user, displayPref = 1)
		profile.save()
		user.email = username
		user.is_active = True
		user.save()