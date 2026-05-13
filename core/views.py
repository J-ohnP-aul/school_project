from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'core/home.html')

def about(request):
    school = SchoolInfo.objects.first()
    staff = Staff.objects.all()
    facilities = Facility.objects.all()

    context = {
        'school': school,
        'staff': staff,
        'facilities': facilities,
    }

    return render(request, 'core/about.html', context)