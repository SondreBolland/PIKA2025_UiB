import smtplib
import time
from email.message import EmailMessage
from flask import render_template

class Mailer:
    def __init__(self):
        self.s = smtplib.SMTP('localhost')

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.s.quit()
        return False

    def send(self, mail):
        msg = EmailMessage()
        msg.set_content(mail.text)
        msg.add_alternative(mail.html, subtype='html')

        msg['Subject'] = mail.subject
        msg['From'] = 'survey@fprg.se'
        msg['To'] = mail.to

        self.s.send_message(msg)

class Mail:
    def __init__(self, to, subject, template, **keywords):
        self.to = to
        self.subject = subject
        self.text = render_template(template + '.txt', **keywords)
        self.html = render_template(template + '.html', **keywords)

    def __repr__(self):
        return self.to + ": " + self.subject + "\n" + self.text

def send_mails(mails):
    with Mailer() as m:
        for mail in mails:
            time.sleep(2)
            # print("Sending mail {}".format(mail))
            m.send(mail)
