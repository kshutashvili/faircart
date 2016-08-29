from django.shortcuts import render
from django.views.generic import View
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

from users.forms import RegForm, ContactVerificationForm
from users.models import ContactVerification


class VerifiedPhoneRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        verifications = request.user.contact_verifications.verified(
            type=ContactVerification.TYPE.PHONE
        )
        if verifications.count() == 0:
            return render(request, 'users/verification_required.html')
        return super(VerifiedPhoneRequiredMixin, self)\
            .dispatch(request, *args, **kwargs)


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


class VerifyContactView(LoginRequiredMixin, View):
    form_class = ContactVerificationForm

    def get_code(self, **kwargs):
        kwargs['type'] = self.kwargs['ctype']
        kwargs['user'] = self.request.user
        try:
            return ContactVerification.objects.verifiable().get(**kwargs)
        except ContactVerification.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        if request.user.is_contact_verified(self.kwargs['ctype']):
            return render(self.request, 'users/verify_contact/result.html')

        code = self.get_code()
        if not code:
            code = ContactVerification.objects.create(
                user=request.user,
                type=self.kwargs['ctype']
            )
        return render(self.request,
                      'users/verify_contact/form.html',
                      {'code': code, 'form': self.form_class()})

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=self.request.POST)
        code = self.get_code()
        if code is None:
            context = {'title': _('Contact validation'),
                       'msg': _('There is no any codes for this contact.')}
            return render(self.request, 'main/message.html', context,
                          status=400)
        if form.is_valid():
            if code.code == form.cleaned_data['code']:
                code.set_verified()
                return render(self.request, 'users/verify_contact/result.html')
            else:
                code.errors += 1
            code.save()
            form.add_error('code', 'No such code')
        return render(self.request, 'users/verify_contact/form.html',
                      {'form': form, 'code': code}, status=400)
