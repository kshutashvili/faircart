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
