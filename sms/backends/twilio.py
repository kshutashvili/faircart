from __future__ import absolute_import
from twilio.rest import TwilioRestClient

from sms.backends.base import BaseBackend


class TwilioBackend(BaseBackend):
    def __init__(self, **options):
        super(TwilioBackend, self).__init__(**options)
        self.client = TwilioRestClient(account=self.options['account_sid'],
                                       token=self.options['auth_token'])

    def send(self, msg, to, sender=None):
        self.client.messages.create(body=msg, to=to,
                                    from_=sender or self.default_sender)
