# Imports
from django.core.management.base import BaseCommand, CommandError
from django.core import mail
from polls.models import *
from django.shortcuts import render, get_object_or_404, redirect

class Command(BaseCommand):
	help = 'Sends an email from oprahprogramtest@gmail.com'

	def add_arguments(self, parser):
		parser.add_argument('question_id', nargs='+', type=int)

	def handle(self, *args, **options):
		#Get question from database
		question = get_object_or_404(Question, pk=20)
		voters = question.question_voters.all()
		r_text = question.reminder_text
		title  = question.question_text
		for voter in voters:
			mail.send_mail('Remember to vote on ' + title,
				r_text,
				'oprahprogramtest@gmail.com',[voter.email])
		# for send_to in options['send_to']:
		# 	mail.send_mail('Please remember to vote on poll',
		# 		'Hello,\n\nYou have been invited to vote on a poll.\n\nSincerely,\nOPRAH Staff',
		# 		'oprahprogramtest@gmail.com',[send_to])