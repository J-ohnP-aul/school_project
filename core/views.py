from django.shortcuts import redirect, render
from .models import SchoolInfo, Staff, Facility, GalleryImage
from news.models import NewsPost


# Create your views here.

def home(request):
    latest_news = NewsPost.objects.order_by('-created_at')[:3]

    return render(request, 'core/home.html', {
        'latest_news': latest_news
    })

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

def contact(request):
    return render(request, 'core/contact.html')

def gallery_view(request):
    images = GalleryImage.objects.all().order_by('-uploaded_at')
    return render(request, 'core/gallery.html', {'images': images})

# admin gallery delete view
def gallery_del(request, pk):
    image = GalleryImage.objects.get(id=pk)
    image.delete()
    return redirect('gallery')