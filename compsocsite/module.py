from polls.models import *
from appauth.models import *

def callbackfunction(tree):
	username = tree[0][0].text.lower() + "@rpi.edu"
	print(username)
	# user, user_created = User.objects.get_or_create(username=username)
	# try:
	# 	var = user.userprofile
	# except:
	# 	profile = UserProfile(user = user, displayPref = 1)
	# 	profile.email = username
	# 	profile.save()
	# 	user.is_active = True
	# 	user.save()