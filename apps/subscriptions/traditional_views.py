from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


@login_required(login_url='/accounts/login/')
def subscription_list(request):
    return HttpResponse('Subscriptions web pages are not implemented yet.')


@login_required(login_url='/accounts/login/')
def subscription_create(request):
    return HttpResponse('Subscription create web page is not implemented yet.')


@login_required(login_url='/accounts/login/')
def subscription_update(request, pk):
    return HttpResponse('Subscription update web page is not implemented yet.')
