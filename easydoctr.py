from google.appengine.api import users
import urllib
import webapp2
import cgi
import json
import requests
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import mail


#message model
class Message(ndb.Model):
	Mail_Id = ndb.StringProperty() 
	To = ndb.StringProperty()
	From = ndb.StringProperty()
	Cc = ndb.StringProperty()
	Subject = ndb.StringProperty()
	Message_Content = ndb.StringProperty()


#patient model
class Patient(ndb.Model):
	Id = ndb.StringProperty(required=True)
	Name = ndb.StringProperty(required=True)
	Mobile_Num = ndb.StringProperty()
	Email_Address = ndb.StringProperty()
	DOB = ndb.StringProperty()
	#Sent_Mails = ndb.StructuredProperty(Message, repeated=True)



#Save the given patient if that patient does not exist in database
def SavePatientData(pat):
	patients = Patient.query()
	isPatientExist = False
	
	for p in patients:
		if p.Id == pat.Id:
			isPatientExist = True

	if isPatientExist == False:
		pat.put()



# def send_simple_message():
#     return requests.post(
#         "https://api.mailgun.net/v2/samples.mailgun.org/messages",
#         auth=("api", "key-484575zwsy10v23tqqc5droje97r-7n8"),
#         data={"from": "Excited User <postmaster@sandbox3948.mailgun.org>",
#               "to": ["adarshrajurs@gmail.com"],
#               "subject": "Hello",
#               "text": "Testing some Mailgun awesomeness!"})


#Send the message to all recipients and save that message to database
def send_mail_gmail(mail_cont):
	user = users.get_current_user()
	for Pat in mail_cont['To']:
		message = mail.EmailMessage()
		message.sender = user.email()
		message.to = Pat['email'] # "adarshrajurs@gmail.com" #
		message.body = mail_cont['email_text']
		message.send()
		msg = Message(Mail_Id = Pat['email'],To = Pat['email'],From = user.email(),Subject = mail_cont['email_sub'],Message_Content = mail_cont['email_text'])
		msg.put()


#Main handler
class MainPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user is None:
			login_url = users.create_login_url(self.request.path)
			self.redirect(login_url)
			return

		sock = urllib.urlopen("https://patients.apiary.io/patients")
		data = json.loads(sock.read())
		sock.close()
		

		for pat in data['items']:
			p = Patient()
			p.Id = pat['id']
			p.Name = pat['name']
			p.Mobile_Num = pat['mobile']
			p.Email_Address = pat['email']			
			p.DOB = pat['dob']			
			SavePatientData(p)			


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


# handler to send and save new messages
class Send(webapp2.RequestHandler):	
	def post(self):
		data = json.loads(self.request.get('mail'))
		send_mail_gmail(data)			
		

application = webapp2.WSGIApplication([
		('/',MainPage),('/sendMessage',Send)], debug=True)