from django.shortcuts import render
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login
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


class VerifyContactView(LoginRequiredMixin, FormView):
    template_name = 'users/verify_contact.html'
    form_class = ContactVerificationForm

    def get_context_data(self, **kwargs):
        kwargs['ctype'] = self.kwargs['ctype']
        return super(VerifyContactView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        code = form.cleaned_data['code']
        try:
            code = self.request.user.contact_verifications.verifiable()\
                .get(code=code, type=self.kwargs['ctype'])
        except ContactVerification.DoesNotExist:
            status = 400
        else:
            code.set_verified()
            code.save()
            status = 200
        context = self.get_context_data(success=status==200, form=None)
        return self.render_to_response(context=context, status=status)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form),
                                       status=400)
