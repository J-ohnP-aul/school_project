from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Applicant
from .forms import ApplicantForm

# Create your views here.


def apply(request):

    if request.method == 'POST':
        form = ApplicantForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Application submitted successfully.'
            )
            return redirect('apply')
    else:
        form = ApplicantForm()
    return render(request, 'admissions/apply.html', {
        'form': form
    })