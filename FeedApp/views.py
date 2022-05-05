from django.shortcuts import render, redirect
from .forms import PostForm, ProfileForm, RelationshipForm
from .models import Post, Comment, Like, Profile, Relationship
from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.http import Http404


# Create your views here.

# When a URL request matches the pattern we just defined,
# Django looks for a function called index() in the views.py file.


def index(request):
    """The home page for Learning Log."""
    return render(request, "FeedApp/index.html")


# decorator - prevent unauthorized access to pages
# must be logged in to access these functions
@login_required
def profile(request):
    # do they have a profile?
    # can't use get() bc doesnt work with exists
    profile = Profile.objects.filter(user=request.user)
    if not profile.exists():
        Profile.objects.create(user=request.user)
    # now that we know they have a profile we can get them
    profile = Profile.objects.get(user=request.user)

    # load this users specific profile so they can add/edit their info (GET)
    if request.method != "POST":
        form = ProfileForm(instance=profile)
    # trying to save to database (POST)
    else:
        form = ProfileForm(instance=profile, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("FeedApp:profile")

    context = {"form": form}
    return render(request, "FeedApp/profile.html", context)


@login_required
# see all post, likes, and comments
def myfeed(request):
    comment_count_list = []
    like_count_list = []
    # grab all posts for this user by filtering username and sort by newest post
    posts = Post.objects.filter(username=request.user).order_by("-date_posted")
    # get like and comments for each post
    for p in posts:
        c_count = Comment.objects.filter(post=p).count()
        l_count = Like.objects.filter(post=p).count()
        comment_count_list.append(c_count)
        like_count_list.append(l_count)

    # zip all info together for easier passing to context
    zipped_list = zip(posts, comment_count_list, like_count_list)

    context = {"posts": posts, "zipped_list": zipped_list}
    return render(request, "FeedApp/myfeed.html", context)
