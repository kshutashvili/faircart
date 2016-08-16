from django.http import HttpResponseRedirect

try:
    from faircart.settings import LOGIN_REDIRECT_URL
except:
    LOGIN_REDIRECT_URL = '/'

try:
    from faircart.settings import URL_LOGIN_REDIRECT
except:
    URL_LOGIN_REDIRECT = ()


class UserRedirectMiddleware():
    def process_response(self,request,response):
        print(request.path)
        if request.path in URL_LOGIN_REDIRECT and request.user.is_authenticated():
            return HttpResponseRedirect(LOGIN_REDIRECT_URL)
        return response