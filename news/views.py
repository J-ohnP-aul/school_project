from django.shortcuts import redirect, render, get_object_or_404
from .models import NewsPost
from django.contrib.auth.decorators import login_required

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