from django.shortcuts import redirect, render, get_object_or_404
from .models import NewsPost
from django.contrib.auth.decorators import login_required
from .forms import NewsPostForm

# Create your views here.

def news_list(request):
    posts = NewsPost.objects.order_by('-created_at')

    return render(request, 'news/news_list.html', {
        'posts': posts
    })


def news_detail(request, slug):
    post = get_object_or_404(NewsPost, slug=slug)

    return render(request, 'news/news_detail.html', {
        'post': post
    })
#admin
@login_required
def news_del(request, pk):
    post = get_object_or_404(NewsPost, id=pk)
    post.delete()
    return redirect('news_list')

@login_required
def news_create(request):
    if request.method == 'POST':
        form = NewsPostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('news_list')
    else:
        form = NewsPostForm()
    return render(request, 'news/news_create.html', {'form': form})

def news_update(request, pk):
    post = get_object_or_404(NewsPost, id=pk)
    if request.method == 'POST':
        form = NewsPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('news_detail', slug=post.slug)
    else:
        form = NewsPostForm(instance=post)
    return render(request, 'news/news_update.html', {'form': form, 'post': post})