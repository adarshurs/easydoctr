from google.appengine.api import users
import urllib
import webapp2
import cgi
import json
import base64
import requests
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
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

#Basic Authentication for preventing unauthenticated users

def basicAuth(func):
	def callf(webappRequest, *args, **kwargs):
		auth_header = webappRequest.request.headers.get('Authorization')

		if auth_header == None:
			webappRequest.response.set_status(401,message="Authorization Required!")
			webappRequest.response.headers['WWW-Authenticate'] = 'Basic realm = "doctor 1234"'

		else:
			auth_parts = auth_header.split(' ')
			user_pass_parts = base64.b64decode(auth_parts[1]).split(':')
			user_arg = user_pass_parts[0]
			pass_arg = user_pass_parts[1]
  
			if user_arg != "pmail" or pass_arg != "doctor1234":
				webappRequest.response.set_status(401, message="Authorization Required")
				webappRequest.response.headers['WWW-Authenticate'] = 'Basic realm="Secure Area"'        
				webappRequest.response.out.write('Authorization failed!')
			else:
				return func(webappRequest, *args, **kwargs)
	return callf



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



# class Mailgun(object):	
# 	def __init__(self):
# 		self.url = "https://api.mailgun.net/v2/samples.mailgun.org/messages"
# 		self.key = "key-484575zwsy10v23tqqc5droje97r-7n8"
# 		self.deadline = 5 
		
# 	def send_mail(self,to,subject,text):
# 		payload = {}
# 		payload['from'] =  "postmaster@sandbox3948.mailgun.org"
# 		payload['to'] = "adarshrajurs@gmail.com"
# 		payload['subject'] = subject
# 		payload['text'] = text
# 		encoded_payload = urllib.urlencode(payload)
# 		base64string = base64.encodestring('api:' + self.key).replace('\n','')
# 		headers = {}
# 		headers['Authorization'] = "Basic %s" % base64string
# 		result = urlfetch.fetch(self.url, deadline=self.deadline, payload=encoded_payload, method=urlfetch.POST, headers=headers)
# 		return result


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
	@basicAuth
	def get(self):
		user = users.get_current_user()
		if user is None:
			login_url = users.create_login_url(self.request.path)
			self.redirect(login_url)
			return

		try:
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

		except Exception, e:
				e = ''
		

		patients = Patient.query()
		# for p in patients:
		# 	p.key.delete()
		#patients = Patient.query()
		all_emails = Message.query()

		
		template_values = {
			'patients':patients,
			'all_mails' : all_emails			
		}
		
		self.response.write(template.render("index.html",template_values))


# handler to send and save new messages
class SendMessage(webapp2.RequestHandler):
	@basicAuth
	def post(self):
		data = json.loads(self.request.get('mail'))
		send_mail_gmail(data)
		
		#send_simple_message()
		
# class DeleteAllMessages(webapp2.RequestHandler):
# 	@basicAuth
# 	def post(self):
# 		all_emails = Message.query()
# 		# for m in all_emails:
# 		# 	m.key.delete()

# 		self.redirect('/?')
		

application = webapp2.WSGIApplication([
		('/',MainPage),('/sendmessage',SendMessage)], debug=True)