import importlib

from django.conf import settings


def get_backend():
    """Returns new instance of the current SMS backend
    """
    module, class_name = settings.SMS_BACKEND.rsplit('.', 1)
    module = importlib.import_module(module)
    cls = getattr(module, class_name)
    return cls(**settings.SMS_BACKEND_OPTIONS)


default = get_backend()
