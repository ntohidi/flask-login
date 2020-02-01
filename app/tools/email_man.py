from app import app
from mailer import Message, Mailer

email_info = app.config['EMAILS']['info']


def email_sender(msg):
    sender = Mailer(
        host=email_info['smtp'][0], port=email_info['smtp'][1], use_tls=True,
        usr=email_info['auth'][0], pwd=email_info['auth'][1]
    )
    return sender.send(msg)


def send_email(user_email="", html="", subject=""):
    msg = Message(From="Nasrin", To=user_email, charset="utf-8")
    msg.Subject = subject
    msg.Body = subject
    msg.Html = html

    return email_sender(msg)


def send_email_with_file(user_email="", html="", subject="", file_path=""):
    msg = Message(From="Nasrin", To=user_email, charset="utf-8")
    msg.Subject = subject
    msg.Body = subject
    msg.Html = html
    msg.attach(file_path)

    return email_sender(msg)


###################################################################################################
# How to use
# data = {
#     'name': "nasrin",
#     'email': 'nasrin@kidocoe.com'
# }
# html = render_template("emails/something.html", data=data)
# send_email(subject="Thanks For Registering for workshop", html=html, user_email=data['email'])
