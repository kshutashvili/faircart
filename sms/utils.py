from sms.backends import default as default_sms_backend


def send_sms(msg, to, sender=None):
    default_sms_backend.send(msg, to, sender=sender)
