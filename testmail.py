import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

msg = MIMEMultipart()

to_email = 'kisell22@yandex.ru'

message = 'TEst'

msg.attach(MIMEText(message, 'plain'))

server = smtplib.SMTP('smtp.gmail.com: 587')

server.starttls()
from_email = 'kkiniuss03@gmail.com'
password = 'szxiluwgluqukdcz'
server.login(from_email, password)
server.sendmail('certificado.supp@gmail.com', to_email, msg.as_string())
server.quit()