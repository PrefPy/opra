# OPRA: Online Preference Reporting and Allocation
Maggie Borkowski and Tyler Johnston's final project for Computational Social Choice, Spring 2016


This project is a web app that assists in the assignment of presentations to students. It allows students to rank their preferences for a presentation topic and presentation date. When all students have input their preferences, it algorithmically allocates topics and presentation dates for all students.

The web app is built on Django, and uses an SQLite database. [Click here](https://docs.djangoproject.com/en/1.9/) for more information on how Django works.


##Models
The following models are used to organize information:
* **Student:** includes a student's name and email address
* **Question:** includes the text of a question, its publication date, and whether it is a follow-up to another question
* **Item:** an option within a question that can be ranked by users. Includes the text of the item and the question it is associated with
* **Response:** the response of one student to one question. Includes a dictionary of the input preferences, the question and student it is associated with, the submission timestamp, and the item from this response the student has been allocated. This last field starts out blank, and is updated when an allocation algorithm is run
* **Dictionary:** a helper model with all the functionality of a Python dictionary. Includes the response it is associated with
* **KeyValuePair:** a helper model for key-value pairs in the dictionary model. The key is an item of a question and the value is the ranking the student assigned to that item


##Admin-Side Usage
The administrator can add, view, edit, and delete questions, items, and students. Currently the administrator can only view and delete responses, but this will be changed in the future to allow full access. All lists of data are sortable by name and (when applicable) date.

To display a question for students to respond to, the administrator must make a new question, entering the relevant text and items. If the question is a follow-up to another question (e.g. date preference is a follow-up to topic preference), the question that preceded it should be selected in the "follow-up" drop-down menu. The question will be publicly viewable starting on the publication date and time specified by the administrator. In the Students section, the administrator must add each student in the class, filling in a name and email address. If the administrator does not add a student, the student will not be able to respond to questions.

The administrator can look in the Responses section to see which students have responded to which questions. When you wish to allocate the items for a question, filter the Responses section to only view responses to that question, then select all responses. Lastly, from the drop-down menu at the top, select the admin action corresponding to the desired allocation algorithm. This will run the algorithm, update the allocated item field in each response, and publish the results.


##Student-Side Usage
From the home page (/polls/), all available questions may be viewed. To view a specific question, click on it. The screen will show the question with a radio grid containing all the items as rows and a number of ranks equal to the number of items as columns. One rank per item may be selected. Ties are allowed, and if desired, it is possible to report no preference for a given item by not selecting a radio button in that row. Beneath this section, there is a drop-down menu to select a student name that should be associated with the reported preferences. A question response may not be submitted without choosing a name. When the "Submit" button is clicked, a response will be submitted, associated with the given question and the selected student name, and with the preferences indicated in the radio button grid. The student will be redirected to a confirmation screen.

Also on the home page is a list of links to results for each question. A given link will not be clickable until the results for that question have been published by the administrator (by performing the allocation algorithm action). Clicking on a link to a set of results will bring the student to a list of all students and the item they have been allocated for that particular question.


##Allocation Algorithms
The project is currently equipped with a serial dictatorship allocation algorithm. This algorithm chooses presentation topic assignment in increasing order of presentation topic response timestamp, then chooses presentation date assignment in decreasing order of presentation topic response timestamp.

More algorithms can easily be added. Within the algorithms.py file inside the polls directory, add a function def for the desired algorithm, with the response set as a parameter. Then, at the top of the admin.py file inside the polls directory, add a function def for an admin action corresponding to the new algorithm. The preexisting admin action function can be used as a guide for the necessary syntax to add a new admin action. Lastly, in the ResponseAdmin class at the bottom of admin.py, add the new admin action function to the list of actions.


##Future Additions
* **User Authentication:**
	Students will be able to create password-protected user accounts, and will use these instead of selecting their names from a drop-down menu when responding to questions. This will reduce the risk of response forgery.
* **Automated Emailing:**
	Students will automatically be notified via email when new questions or results have been published.
* **Project Containers:**
	The administrator will be able to group questions into containers, such as all the questions that belong to a particular project, or all the questions for a given semester of a course. Students will be able to view the questions and results grouped together accordingly.
* **Aesthetic Improvements:**
	Template files for the student-side views will be updated to be more aesthetically pleasing. Additionally, a third party can easily add or modify their own templates, available in the /polls/templates directory of the project.
