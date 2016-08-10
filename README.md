# OPRA: Online Preference Reporting and Aggregation

This project is a web app that assists in the assignment of presentations to students. It allows students to rank their preferences for a presentation topic and presentation date. When all students have input their preferences, it algorithmically allocates topics and presentation dates for all students.

The web app is built on Django, and uses an SQLite database. [Click here](https://docs.djangoproject.com/en/1.9/) for more information on how Django works.

##Installation
* **For Windows**:

1. Install [Python](https://www.python.org/downloads/). It is recommended that you use the latest version of Python 3 (as of now, 3.4 or 3.5).
2. Install [Django](https://www.djangoproject.com). The easiest way to do this is through pip, which can be found [here] (https://pip.pypa.io/en/latest/installing/#installing-with-get-pip-py). Then you can install django simply by entering the command: 

   <code>pip install django</code>
3. Install the dependencies listed below in the Dependencies section.
4. Clone this project from Github
5. To run the project, you open the command line (terminal), change to the current directory of the project. Then in the root of the project, enter the following commands:
  
  <code>cd composcite</code>
  
  <code>python3 manage.py runserver</code>

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
    You can verify by entering the command:

    <code> import django </code>

    <code> print(django.get_version()) </code>
3. Install the dependencies listed below in the Dependencies section by entering:

    <code>  pip install Package-Name </code>
4. Clone this project from Github (You can download Github Desktop for Mac or clone this project direclt from Github Website.)
5. To run the project, you open the command line (terminal), change to the current directory of the project. Then in the root of the project, enter the following commands:

    <code>cd composcite</code>
    
    <code>python3 manage.py runserver</code>


##Dependencies
* **Django-mathfilters**:
* **Django-mobile**:
* **pillow**:

##Models
The following models are used to organize information:
* **Student:** includes a student's name and email address
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

