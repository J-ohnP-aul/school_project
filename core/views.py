from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import SchoolInfo, Staff, Facility, GalleryImage
from news.models import NewsPost
from .forms import FacilityForm, GalleryImgForm


# Create your views here.

def home(request):
    latest_news = NewsPost.objects.order_by('-created_at')[:3]
    facilities = Facility.objects.all()

    return render(request, 'core/home.html', {
        'latest_news': latest_news,
        'facilities': facilities,
    })

def about(request):
    school = SchoolInfo.objects.first()
    staff = Staff.objects.all()

    context = {
        'school': school,
        'staff': staff,
    }

    return render(request, 'core/about.html', context)



def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            from django.contrib import messages as msg
            msg.success(request, f'Thank you, {name}! We have received your message and will get back to you soon.')
        
    return render(request, 'core/contact.html')

def gallery_view(request):
    images = GalleryImage.objects.all().order_by('-uploaded_at')
    return render(request, 'core/gallery.html', {'images': images})

# admin gallery delete view
def gallery_del(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    image.delete()
    return redirect('gallery')

@login_required
def gallery_create(request):
    if request.method == 'POST':
        form = GalleryImgForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gallery')
    else:
        form = GalleryImgForm()
    return render(request, 'core/gallery_create.html', {'form': form})

def gallery_update(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    if request.method == 'POST':
        form = GalleryImgForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            return redirect('gallery')
    else:
        form = GalleryImgForm(instance=image)
    return render(request, 'core/gallery_form.html', {'form': form})


def facilities(request):
    facilities = Facility.objects.all()
    return render(request, 'core/facilities.html', {
        'facilities': facilities,
    })

def facility_create(request):
    if request.method == 'POST':
        form = FacilityForm(request.POST, request.FILES)  # ✅ Added request.FILES
        if form.is_valid():
            form.save()
            return redirect('facilities')
    else:
        form = FacilityForm()
    return render(request, 'core/facility_create.html', {'form': form})

def facility_update(request, pk):
    facility = get_object_or_404(Facility, pk=pk)
    if request.method == 'POST':
        # ✅ CORRECT - also needs request.FILES
        form = FacilityForm(request.POST, request.FILES, instance=facility)
        if form.is_valid():
            form.save()
            return redirect('facilities')
    else:
        form = FacilityForm(instance=facility)
    return render(request, 'core/facility_form.html', {'form': form})

def facility_del(request, pk):
    facility = get_object_or_404(Facility, pk=pk)
    facility.delete()
    return redirect('facilities')

