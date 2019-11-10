from collections import defaultdict, deque

class Matcher:

	#constructs a Matcher instance
	
	#studentPrefs is a dict from student to class ranking as a list
	#e.g. "student1" -> ["class1", "class3", "class2"]
	#the ranking doesn't need to be complete
	#all missing classes are treated as "worse than nothing"
	
	#studentFeatures is a dict from student to dict(class -> feature vector)
	#e.g "student1" -> {"class1" -> (0, 1, 3.8), "class2" -> (1, 2, 3.8)}
	#that is, studentFeatures[s][c] is student s's feature vector in terms of class c
	#each student needs to have a feature vector for each class in their ranking
	
	#classCaps is a dict from class to maximum capacity
	#e.g. "class1" -> 5
	
	#classFeatures is a dict from class to feature vector
	#e.g. "class1" -> (98, 70, 65)
	
	#the dot product of a student's feature vector with a particuar class's feature vector is its score
	#in terms of that class
	def __init__(self, studentPrefs, studentFeatures, classCaps, classFeatures):
	
		self.studentPrefs = studentPrefs
		self.classCaps = classCaps
	
	
		#a student may not have a feature vector for every class
		#in that case, we convert all the inner dict(class -> vector) objects to defaultdicts
		#that way, if we make a call studentFeatures[s][c], but student s doesn't have a feature vector for class c,
		#instead of getting a ValueError, we get an empty tuple ()
		#doing a dot product with an empty tuple will give a score of 0, which is what we want
		studentFeatures = {s: defaultdict(tuple, d) for s, d in studentFeatures.items()}
	
		#dot product of a and b
		#only does dot over the first min(len(a), len(b)) elements
		def dot(a, b):
			#it's ok if lengths aren't equal, will just take shortest length,
			#so we don't really need this assert
			#assert len(a) == len(b)
			return sum(x*y for x, y in zip(a, b))
		
		#returns a complete ranking over students for one specific class c
		def makeClassPref(c):

			#return list of students, sorted by dot product, then student name (for tiebreaking)
			#if a student doesn't have a feature vector for this class, we will get (), which will make their score 0
			return sorted(studentPrefs.keys(), key=lambda s: (dot(classFeatures[c], studentFeatures[s][c]), s), reverse=True)
		
		#call makeClassPref on each class to make the preferences
		self.classPrefs = {c: makeClassPref(c) for c in classFeatures.keys()}
		
		
		#output variables
		self.studentMatching = {} #student -> class
		self.classMatching = defaultdict(list) #class -> [students]

		#we index preferences at initialization to avoid expensive lookups when matching
		self.classRank = defaultdict(dict) #classRank[c][s] is c's ranking of s
		self.studentRank = defaultdict(dict) #studentRank[s][c] is s's ranking of c
		
		#if ranking isn't present, treated as less than none
		
		for c, prefs in self.classPrefs.items():
			for i, s in enumerate(prefs):
				self.classRank[c][s] = i

		for s, prefs in studentPrefs.items():
			for i, c in enumerate(prefs):
				self.studentRank[s][c] = i

				
	
	#Test whether s prefers c over c2.
	def prefers(self, s, c, c2):
		ranking = self.studentRank[s]
		
		if c in ranking:
		
			if c2 in ranking:
				#both in ranking
				
				#return normally
				return ranking[c] < ranking[c2]
			
			else:
				#c in ranking, but c2 not in ranking
				
				#c is preferred
				return True
			
		else:	
			if c2 in ranking:
				#c not in ranking, but c2 in ranking
			
				#c2 is preferred
				return False
			
			else:
				#both not in ranking
				
				#none, none: false
				#strr, none: false
				#none, strr: true
				#strr, strr: c < c2
				
				#None represents no one. it can be thought of as being after the last ranked element,
				#and before the unranked ones
				
				if c2 == None:
					#either c is str and c2 is none, or both none
					#either way, c is not preferred over c2
					return False
					
				if c == None:
					#c is none and c2 is str
					#so c, being no one, is preferred over unranked c2
					return True
				
				
				#if we get here, none isn't involved
				#both c and c2 are unranked str's
			
				#preference based on alphabetical order
				return c < c2
				

	#Return the student favored by c after s.
	def after(self, c, s):
	
		#TODO extra checking here might not be needed as classes have full ranking
		
		if s not in self.classRank[c]:
			#TODO will this happen? probably not
			print(f"student {s} is not in {c}'s ranking")
			#assert False
			
			#in case it does happen,
			#we return the next alphabetical student who is also not ranked
			#it is expensive though
			
			students = sorted(self.studentPrefs.keys())
			
			#if we're trying to find the next student after "no one",
			#we search from the beginning
			if s == None:
				i = 0
			
			else:
				i = students.index(s)+1
				
			while i < len(students) and students[i] in self.classRank[c]:
				i += 1
				
				
			if i >= len(students):
				#this alg in't perfect. we're mixing what None means
				#none usually means "no one"
				#but here it means there isn't a next student
				#this probably doesn't matter much, as this code will probably not be used
				return None
				
			print(f"using {students[i]}")
			return students[i]
	
		#index of student following s in list of prefs
		i = self.classRank[c][s] + 1
		
		if i >= len(self.classPrefs[c]):
			#no other students are prefered.
			return None
		
		return self.classPrefs[c][i]
		
	
		
	#Try to match all classes with their next preferred spouse.
	#does class-proposing Gale-Shapely
	def match(self):
	
		#simple combination of a queue with a set
		#the set is used for quick "contains" lookups
		class SmartQueue:
		
			def __init__(self):
				self.queue = deque()
				self.set = set()
				
			def put(self, x):
				self.queue.append(x)
				self.set.add(x)
				
			def pop(self):
				x = self.queue.popleft()
				self.set.remove(x)
				return x
				
			def __contains__(self, x):
				return x in self.set
				
			def __len__(self):
				return len(self.queue)
	
	
		#classes (full ranking)
		#students (partial ranking)
	
		#queue of classes we still have to match
		queue = SmartQueue()
	
		#next is a map from class to next student to propose to
		#starts as first preferences
		next = {}
	
		#mapping from students to current class
		studentMatching = {}
		
		#the current capacity for each class
		currCap = defaultdict(int)
		
		#initalize
		#we do this in a loop so we only iterate over self.classPrefs once
		for c, rank in self.classPrefs.items():
			#we start with all the classes in the queue
			queue.put(c)
			
			#and all the classes will propose to their top ranking student
			next[c] = rank[0]
		
		
		#while we still have classes to match
		while len(queue) > 0:
		
			#take class off list
			c = queue.pop()
			
			#make proposals for the remaining capacity
			for i in range(self.classCaps[c] - currCap[c]):
			
				#next student for c to propose to
				s = next[c]
				
				#if we run out of students to propose to
				if s == None:
					#we break, finished matching, but having less than max capacity
					break
				
				#student after s in c's list of prefs
				#"next-next" student for c to propose to
				next[c] = self.after(c, s)
				
				
				#if s is already matched
				if s in studentMatching:
				
					#current class that s is in
					c2 = studentMatching[s]
					
					assert c2 != c
					
					#if s prefers c more than current class
					if self.prefers(s, c, c2):
					
						#old class c2 becomes available again
						
						#unmatch to old class
						currCap[c2] -= 1
						
						#if c2 isn't already scheduled to match, put it in the queue
						if c2 not in queue:
							queue.put(c2)
						
						#s becomes matched to c
						studentMatching[s] = c
						currCap[c] += 1
						
						
					#otherwise, we're rejected
					#just go to the next proposal
				
				#else, s is unmatched, so c gets them
				else:
					#s becomes matched to c
					studentMatching[s] = c
					currCap[c] += 1
			
			
			#we finished the proposals for this class for this round
			#now, does this class need another round?
			
			#if we aren't full, and haven't been "none'd", we re-add ourself
			#"none'd" meaning we ran out of students to propose to
			if currCap[c] < self.classCaps[c] and next[c] != None:
				queue.put(c)
			
			
		#now we've matched all classes, so we're done
		
		#populate studentMatching
		self.studentMatching = studentMatching
		
		#populate classMatching from studentMatching
		for s, c in studentMatching.items():
			self.classMatching[c].append(s)
			

		return self.classMatching

	#check if the mapping of studentMatching to husbands is stable
	#TODO this doesn't look at unmatched students or classes. is that a problem?
	def isStable(self, studentMatching=None, verbose=False):
	
		if studentMatching is None:
			studentMatching = self.studentMatching
			
		for s, c in studentMatching.items():
		
			i = self.classRank[c][s]
			
			preferred = self.classPrefs[c][:i]
			
			for p in preferred:
				
				#it's possible p is unmatched
				#in that case, c2 is None
				c2 = None	
				if p in studentMatching:
					c2 = studentMatching[p]
				
				#check if p prefers us over current matching
				#if c2 is none, this just checks if p prefers us to nobody
				if self.prefers(p, c, c2):
					if verbose:
						print(f"{c}'s marriage to {s} is unstable:\n{c} prefers {p} over {s} and {p} prefers {c} over her current husband {c2}")
					return False
		return True
