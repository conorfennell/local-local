from django.http import HttpResponse
from django.shortcuts import render

def home_age_view(request):
    return HttpResponse("Homepage 3")
