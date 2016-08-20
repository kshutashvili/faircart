from django.shortcuts import render, redirect


def landing(request):
    if request.user.is_authenticated():
        # We need this redirect while we have no landing.
        return redirect('transfer')
    return render(request, 'main/landing.html')
