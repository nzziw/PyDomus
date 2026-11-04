from django.shortcuts import render
from django_otp.decorators import otp_required

# Create your views here.
@otp_required
def home_view(request):
    return render(request, 'dashboard/index.html')
