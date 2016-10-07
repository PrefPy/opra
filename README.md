# OPRA: Online Preference Reporting and Aggregation

This project is a web app that assists in the assignment of presentations to students. It allows students to rank their preferences for a presentation topic and presentation date. When all students have input their preferences, it algorithmically allocates topics and presentation dates for all students.

The web app is built on Django, and uses an SQLite database. [Click here](https://docs.djangoproject.com/en/1.9/) for more information on how Django works.

##Installation
* **For Windows**:

1. Install [Python](https://www.python.org/downloads/). It is recommended that you use the latest version of Python 3 (as of now, 3.4 or 3.5).
2. Install [Django](https://www.djangoproject.com). The easiest way to do this is through [pip] (https://pip.pypa.io/en/latest/installing/#installing-with-get-pip-py). Then you can install django simply by entering the command: 

   <code>pip install django</code>
   
   You can verify installation by entering the command:
   
   <code> import django </code>
   
   <code> print(django.get_version()) </code>
    
3. Install the dependencies listed below in the Dependencies section.
4. Clone this project from Github
5. To run the project, you open the command line (terminal), change to the current directory of the project. Then in the root of the project, enter the following commands:
  
  <code>cd composcite</code>
  
  <code>python3 manage.py runserver</code>

6. To view the page, go to your web browser and visit this address:

  <code>http://127.0.0.1:8000</code>

* **For Mac**:

1. Install [Python](https://www.python.org/downloads/). It is recommended that you use the latest version of Python 3 (as of now, 3.4 or 3.5). For Mac, the default python version is python 2. You can check your python version by entering the command in terminal:

    <code> python -V </code>

    or 

    <code> python3 -V </code>

2. Install [Django](https://www.djangoproject.com). The easiest way to do this is through pip. You can install pip by entering the command in terminal:

    <code> sudo easy_install pip </code>

    More about pip can be found [here] (https://pip.pypa.io/en/latest/installing/#installing-with-get-pip-py).
    Then you can install django simply by entering the command: 

    <code>pip install django</code>

    You can verify installation by entering the command:

    <code> import django </code>

    <code> print(django.get_version()) </code>
3. Install the dependencies listed below in the Dependencies section by entering:

    <code>  pip install Package-Name </code>
4. Clone this project from Github (You can download Github Desktop for Mac or clone this project direclt from Github Website.)
5. To run the project, you open the command line (terminal), change to the current directory of the project. Then in the root of the project, enter the following commands:

    <code>cd composcite</code>
    
    <code>python3 manage.py runserver</code>
6. To view the page, go to your web browser and visit this address:

    <code>http://127.0.0.1:8000</code>

##Dependencies
* **Django-mathfilters**:
* **Django-mobile**:
* **pillow**:
* **prefpy**:

##Models
The following models are used to organize information:
* **User:** includes username, password, and personalized settings
* **Question:** includes the text of a question, its publication date, and whether it is a follow-up to another question
* **Item:** an option within a question that can be ranked by users. Includes the text of the item and the question it is associated with
* **Response:** the response of one student to one question. Includes a dictionary of the input preferences, the question and student it is associated with, the submission timestamp, and the item from this response the student has been allocated. This last field starts out blank, and is updated when an allocation algorithm is run
* **Dictionary:** a helper model with all the functionality of a Python dictionary. Includes the response it is associated with
* **KeyValuePair:** a helper model for key-value pairs in the dictionary model. The key is an item of a question and the value is the ranking the student assigned to that item


##Poll Owner Usage
The poll owner can add, view, edit, and delete questions, items, and voters. All lists of data are sortable by name and (when applicable) date.

To display a question for users to respond to, the poll owner must make a new question, entering the relevant text and items. The poll owner can look in the history section to see which users have responded to which questions. When you wish to allocate the items for a question, click stop to end the poll.This will run the algorithm, update the allocated item field in each response, and publish the results.

##Voter Usage
From the home page (/polls/), all available questions may be viewed. To view a specific question, click on it. The screen will show a simplfied voter interface, which allows you to visualize your preferences. One rank per item may be selected, but ties are allowed. Only complete preferences are accepted. A question response may either be submitted with a registered account or under an anonymous name, if the poll owner has agreed to allow anonymous voting. When the "Submit" button is clicked, a response will be submitted, associated with the given question, and with the preferences indicated. A small alert will be displayed.

Also on the home page is a list of links to results for each question. A given link will not be clickable until the results for that question have been published by the poll owner (by performing the allocation algorithm action). Clicking on a link to a set of results will bring the student to a list of all students and the item they have been allocated for that particular question.


##Allocation Algorithms
The project is currently equipped with a serial dictatorship allocation algorithm. This algorithm chooses presentation topic assignment in increasing order of presentation topic response timestamp, then chooses presentation date assignment in decreasing order of presentation topic response timestamp.

More algorithms can easily be added. Within the algorithms.py file inside the polls directory, add a function def for the desired algorithm, with the response set as a parameter. Then, at the top of the admin.py file inside the polls directory, add a function def for an admin action corresponding to the new algorithm. The preexisting admin action function can be used as a guide for the necessary syntax to add a new admin action. Lastly, in the ResponseAdmin class at the bottom of admin.py, add the new admin action function to the list of actions.

##OPRA DOCUMENTATON

OPRA stands for online preference reporting and aggregation, which is essentially an online voting system. The system is built up by taking advantage of Django free and open-source web framework written extensively in Python. It maintains Django’s basic model-view-template (MVT) architectural pattern.  This documentation basically consists of two parts. The first part will give you an overarching view of the major components of OPRA. The second part will dive into each component and detail each constituted function. 

**Part I: Bird-view of OPRA**
* **A. The model layer** 
A model is the single, definitive source of information about the data created by the OPRA administrator and users. It contains the essential fields and behaviors of the data you’re storing in the database. In other words, each model maps to a single database table. Essentially, each model is a Python class and each attribute of the class represents a database field. 

* **B. The view layer**
The view layer basically encapsulates the logic responsible for processing a user’s request and for returning the response. It consists of a bunch of view functions, and each function is simply a Python function that takes a Web request and returns a Web response. The response can be the HTML contents of a Web page, or a redirect, or a 404 Error, or an XML document, or an image … or anything. The view itself contains whatever arbitrary logic is necessary to return the response. The code can live anywhere you want, as long as it’s on your Python path. For convenience and safety, the convention is to put all the views in a file called view.py. In order to make the views work well, OPRA also needs an URLs module. This module is pure Python code and is a simple mapping between URL patterns to your view functions. 

* **C. The template layer**
The template layer provides a designer-friendly syntax for rendering the information to be presented to the users. It provides a convenient way to generate HTML dynamically, and contains the static parts of the desired HTML output as well as some special syntax describing how the dynamic content will be inserted. 

##Part II: Dive into OPRA component functions
The outer compsocsite/ root directory is just a container for OPRA. You can rename it without any problems.
•	**manage.py:** A Python command-line utility that lets the user interact with OPRA in various ways. 
•	**Appauth:** This folder is responsible for registering users and login/logout setting. 
•	**Polls:** A Python package for single poll application. Modify this folder if you want to customize this application. 
•	**Multipolls:** Another Python package for multiple poll application. Modify this folder if you want to customize this application. 
•	**Groups:** This folder is responsible for editing group members to vote for a specific subject. The administrator can add or remove voters from the group.
•	**Static:** For image, js, css files.
•	**Compsocsite:** This inner directory is the actual Python package for OPRA. Its name is the Python package name you’ll need to use to import anything inside it. 
•	**Template:** The folder contains a list of configurations, one for each engine.
•	**Stunnel:** 

Roughly speaking, the architecture of each aforementioned folder follows a similar file structure. For instance, you will see the following files in the polls/ directory.
•	Migrations: The folder is created to store database changes as models are updated.  Here are two handy commands to achieve this: python3 manage.py makemigrations </code>, and <code> python3 manage.py migrate </code>.
•	Templates: It contains all the view files, which are a mix of HTML and Django template language. You can customize the display of each file in your browser. 
•	models.py:  It contains all the model (Python class) definitions.
•	urls.py: It contains a list of links displayed in the browser, where each link has its own function. The function can either render the view or perform calculations. 
•	views.py: It contains all the logic required to retrieve data from the database and perform calculations.

Some extra file for each app
•	appauth:
➢	User: Borrowed from Django implementation of User. It stores a user's username, password, email address, etc. For more information on Django implementation of User model, please go to corresponding Django documentation page.
➢	UserProfile: This model is implemented to record global settings for a single user to avoid modifying Django's User model. It is in an one-to-one relationship to User model.	
➢	register: This functions runs when a registration form is submitted. A user instance and a userprofile instance are created if username is valid.
➢	user_login: A function for checking the authenticity of a user's request and processes login information.
➢	displaySettings, globalSettings, updateSettings, disableHint, changePassword: These functions are used in global setting and account setting pages.
			
•	groups:
➢	Group: A group model that links several users together into a group for user's convenience in inviting voters.
➢	Functions: IndexView, AddGroupView, MembersView: Pages for group settings and adding groups. Addgroup, addmember, removemember, deletegroup: Functions used for group settings. AddGroupVoters, removeGroupVoters: Used at group voter invitations.
			
	


