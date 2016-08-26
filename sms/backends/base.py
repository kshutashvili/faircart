from django.contrib.auth import get_user_model


class BaseBackend(object):
    def __init__(self, **options):
        self.default_sender = options.pop('default_sender')
        self.options = options

    def send(self, msg, to, sender=None):
        raise NotImplementedError


class ConsoleBackend(BaseBackend):
    def __init__(self, **options):
        super(ConsoleBackend, self).__init__(**options)
        self.tpl = "{sender} -> {to}: {msg}"

    def send(self, msg, to, sender=None):
        print self.tpl.format(sender=sender or self.default_sender,
                              to=to, msg=msg)


class NullBackend(BaseBackend):
    def send(self, msg, to, sender=None):
        pass


class EmailBackend(BaseBackend):
    def __init__(self, **options):
        super(EmailBackend, self).__init__(**options)
        # We use property to avoid import problems
        self._user_model = None

    @property
    def user_model(self):
        if self._user_model is None:
            self._user_model = get_user_model()
        return self._user_model

    def send(self, msg, to, sender=None):
        try:
            user = self.user_model.objects.get(phone=to)
        except self.user_model.DoesNotExist:
            return
        user.email_user('SMS message', msg)
