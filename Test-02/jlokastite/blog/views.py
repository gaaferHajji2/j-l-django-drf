from django.shortcuts import render
from .models import Post

# Create your views here.
def post_list(request):
    posts = Post.published.all()
    # in this way we avoid positional arguments error
    return render(request, 'blog/post/list.html', {'posts': posts});