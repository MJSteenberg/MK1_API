def send_email(SUBJECT, BODY, SEND_TO):
    from appscript import app, k
    from mactypes import Alias
    from pathlib import Path
    import base64

#     import os
#     f = open(os.path.expanduser(f"~/OneDrive - Mark1 Media & Consulting/Documents - Copy/Datorama/Twitter API/{EXCEL_FILE}.xlsx"))

    def create_message_with_attachment():
        subject = SUBJECT
        body = BODY
        to_recip = SEND_TO
        msg = Message(subject=subject, body=body, to_recip=to_recip)

        # attach file
        p = Path(f'{f.name}')
        msg.add_attachment(p)
        msg.show()
        msg.send()

    class Outlook(object):
        def __init__(self):
            self.client = app('Microsoft Outlook')

    class Message(object):
        def __init__(self, parent=None, subject='', body='', to_recip=[], cc_recip=[], show_=True):

            if parent is None: parent = Outlook()
            client = parent.client

            self.msg = client.make(
                new=k.outgoing_message,
                with_properties={k.subject: subject, k.content: body})

            self.add_recipients(emails=to_recip, type_='to')
            self.add_recipients(emails=cc_recip, type_='cc')

            if show_: self.show()

        def show(self):
    #         self.msg.open()
            self.msg.activate()
    #         

        def send(self):
            self.msg.send()

        def add_attachment(self, p):
            # p is a Path() obj, could also pass string

            p = Alias(str(p)) # convert string/path obj to POSIX/mactypes path

            attach = self.msg.make(new=k.attachment, with_properties={k.file: p})

        def add_recipients(self, emails, type_='to'):
            if not isinstance(emails, list): emails = [emails]
            for email in emails:
                self.add_recipient(email=email, type_=type_)

        def add_recipient(self, email, type_='to'):
            msg = self.msg

            if type_ == 'to':
                recipient = k.to_recipient
            elif type_ == 'cc':
                recipient = k.cc_recipient

            msg.make(new=recipient, with_properties={k.email_address: {k.address: email}})

    return create_message_with_attachment()

send_email(
            SUBJECT='Solidarity Gender THIS HAS TO WORK',
            BODY="Solidarity Gender through script",
            SEND_TO=['mj@mark1.co.za']
          )