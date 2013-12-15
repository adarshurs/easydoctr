from google.appengine.api import users
import urllib
import webapp2
import cgi
import json
import requests
from urlparse import urlparse
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import mail

patients = ""
all_emails = ""


class Message(ndb.Model):
	Mail_Id = ndb.StringProperty() 
	To = ndb.StringProperty()
	From = ndb.StringProperty()
	Cc = ndb.StringProperty()
	Subject = ndb.StringProperty()
	Message_Content = ndb.StringProperty()


class Patient(ndb.Model):
	Id = ndb.StringProperty(required=True)
	Name = ndb.StringProperty(required=True)
	Mobile_Num = ndb.StringProperty()
	Email_Address = ndb.StringProperty()
	DOB = ndb.StringProperty()
	#Sent_Mails = ndb.StructuredProperty(Message, repeated=True)

class SavePatientData:
	def savePatient(self, pat):
		patients = Patient.query()
		isPatientExist = False
		for p in patients:
			if p.Id == pat.Id:
				isPatientExist = True

		if isPatientExist == False:
			pat.put()

	def updatePatientMail(self,patientIds,mail):
		patients = Patient.query()
		for p in patients:
			for pid in patIds:
				if p.Id == pid:
					p.Mails.append(mail)
					p.put()


# def send_simple_message():
#     return requests.post(
#         "https://api.mailgun.net/v2/samples.mailgun.org/messages",
#         auth=("api", "key-484575zwsy10v23tqqc5droje97r-7n8"),
#         data={"from": "Excited User <postmaster@sandbox3948.mailgun.org>",
#               "to": ["adarshrajurs@gmail.com"],
#               "subject": "Hello",
#               "text": "Testing some Mailgun awesomeness!"})

def send_mail_from_gmail(mail):
	user = users.get_current_user()
	message = mail.EmailMessage()
	message.sender = user.email()
	message.to = mail.to
	message.body = mail.body
	message.send()



class MainPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user is None:
			login_url = users.create_login_url(self.request.path)
			self.redirect(login_url)
			return

		#send_mail_from_gmail()

		sock = urllib.urlopen("https://patients.apiary.io/patients")
		data = json.loads(sock.read())
		sock.close()
		strpatient = SavePatientData()

		# mail1 = Message(Mail_Id = "abhinav@practo.com",To = "abhinav@practo.com",From="thisDoctor@practo.com",Cc="",Subject="Next week I'll not be available",Message_Content="Hi Everyone, \n Next week I'm going for a vacation. So those who have check up schedules for next week, please visit me after next week. \n For any emergencies you can contact the clinic at any time.\n  Thank You \n Doctor")
		# mail1.put()

		# mail2 = Message(Mail_Id = "praveen@practo.com",To = "praveen@practo.com",From="thisDoctor@practo.com",Cc="",Subject="Your this month check up is scheduled to",Message_Content="Hi Everyone, \n Next week I'm going for a vacation. So those who have check up schedules for next week, please visit me after next week. \n For any emergencies you can contact the clinic at any time.\n  Thank You \n Doctor")
		# mail2.put()


		for pat in data['items']:
			p = Patient()
			p.Id = pat['id']
			p.Name = pat['name']
			p.Mobile_Num = pat['mobile']
			p.Email_Address = pat['email']			
			p.DOB = pat['dob']			
			strpatient.savePatient(p)			


		patients = Patient.query()

		# for p in patients:
		# 	p.key.delete()
		#patients = Patient.query()
		

		all_emails = Message.query()

		# for m in all_emails:
		# 	m.key.delete()

		# all_emails = Message.query()

		try:
			default_patient = Patient.query(Patient.Id == "1").fetch(1)[0]

		except Exception, e:
			default_patient = ""
		
		template_values = {
			'patients':patients,
			'all_mails' : all_emails			
		}

		#self.response.write(response)
		self.response.write(template.render("index.html",template_values))

class Send(webapp2.RequestHandler):	
	def post(self):
		#mail_to_send = {'To':[],'subject':"",'text':""}
		To = self.request.get('to')
		subject = self.request.get('subject')
		text = self.request.get('text')

		self.response.write(subject);
		# strpatient = SavePatientData()
		# strpatient.updatePatientMail(ids)
		#self.redirect('/?')

class FilterMessages(webapp2.RequestHandler):
	def post(self):
		mail_id = self.request.POST["email"]
		if mail_id:
			MessagesToShow = Message.query(Message.Mail_Id == mail_id).fetch(10)
			all_emails = MessagesToShow

		#all_emails = Message.query()
		patients = Patient.query()
		template_values = {
			'patients':patients,
			'all_mails' : MessagesToShow			
		}

		self.response.write(template.render("index.html",template_values))
		
	
application = webapp2.WSGIApplication([
		('/',MainPage),('/sendMessage',Send),('/getMessages',FilterMessages)], debug=True)