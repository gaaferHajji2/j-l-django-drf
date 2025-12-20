from django.core.paginator import EmptyPage,PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
# from django.http import Http404
from .models import Post

# Create your views here.
def post_list(request):
    post_list = Post.published.all()
    # Pagination with 3 posts per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1);
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(paginator.num_pages)
    # in this way we avoid positional arguments error
    return render(request, 'blog/post/list.html', {'posts': posts});

def post_detail(request, year: int, month: int, day: int, post):
    # post = Post.publish.get(pk=id)
    post = get_object_or_404(
        Post, 
        status=Post.Status.PUBLISHED, 
        slug=post, 
        publish__year=year, 
        publish__month=month,
        publish__day=day
    )

    return render(
        request, 'blog/post/detail.html', {'post': post}
    )