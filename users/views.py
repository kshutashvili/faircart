from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login
from users.forms import RegForm


class RegView(FormView):
    template_name = 'users/reg.html'
    form_class = RegForm
    success_url = '/'

    def form_valid(self, form):
        user = form.save()
        user = authenticate(username=user.phone,
                            password=form.cleaned_data['password1'])
        if user is None:
            pass # TODO: show login error
        else:
            login(self.request, user)
        return super(RegView, self).form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form),
                                       status=400)
