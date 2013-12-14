from google.appengine.api import users
import urllib
import webapp2
import cgi
import json
from urlparse import urlparse
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
#from google.appengine.api import mail

patients = ""
all_emails = ""


class Message(ndb.Model):
	Id = ndb.StringProperty() 
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

class MainPage(webapp2.RequestHandler):
	def get(self):				
		sock = urllib.urlopen("https://patients.apiary.io/patients")
		data = json.loads(sock.read())
		sock.close()
		strpatient = SavePatientData()

		# mail1 = Message(To = "abhinav@practo.com",From="thisDoctor@practo.com",Cc="",Subject="Next week I'll not be available",Message_Content="Hi Everyone, \n Next week I'm going for a vacation. So those who have check up schedules for next week, please visit me after next week. \n For any emergencies you can contact the clinic at any time.\n  Thank You \n Doctor")
		# mail1.put()

		# mail2 = Message(To = "praveen@practo.com",From="thisDoctor@practo.com",Cc="",Subject="Your this month check up is scheduled to",Message_Content="Hi Everyone, \n Next week I'm going for a vacation. So those who have check up schedules for next week, please visit me after next week. \n For any emergencies you can contact the clinic at any time.\n  Thank You \n Doctor")
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
		patients = Patient.query()

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

		#self.response.write(mail1)
		self.response.write(template.render("index.html",template_values))

class Save(webapp2.RequestHandler):	
	def post(self):
		ids = self.request.get['selectedPatientsIds']
		message = self.request.get['message']
		strpatient = SavePatientData()
		strpatient.updatePatientMail(ids)

		


		self.redirect('/?')
		
	
application = webapp2.WSGIApplication([
		('/',MainPage),('/save',Save)], debug=True)