from django.shortcuts import get_object_or_404, render
from django.http import Http404
from .models import Post

# Create your views here.
def post_list(request):
    posts = Post.published.all()
    # in this way we avoid positional arguments error
    return render(request, 'blog/post/list.html', {'posts': posts});

def post_detail(request, id: int):
    try:
        # post = Post.publish.get(pk=id)
        post = get_object_or_404(Post, id=id, status=Post.Status.PUBLISHED)
    except Post.DoesNotExist:
        raise Http404("No post found")
    return render(
        request, 'blog/post/detail.html', {'post': post}
    )