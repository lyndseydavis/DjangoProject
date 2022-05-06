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


# create posts
@login_required
def new_post(request):
    # if a get request then want an empty form for a post
    # if a post request then we want to send to db
    if request.method != "POST":
        form = PostForm()
    else:
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # save but don't commit to db yet bc we want to assign to a user
            new_post = form.save(commit=False)
            new_post.username = request.user
            new_post.save()
            return redirect("FeedApp:myfeed")

    context = {"form": form}
    return render(request, "FeedApp/new_post.html", context)


# add comments
@login_required
def comments(request, post_id):
    # want to see if someone clicked on the comment button
    # have to process everything manually in html since we are not using a form
    # if request is a post method and button has been clicked to submit
    if request.method == "POST" and request.POST.get("btn1"):
        comment = request.POST.get("comment")
        # create a new row in Comment model for db
        Comment.objects.create(
            post_id=post_id,
            username=request.user,
            text=comment,
            date_added=date.today(),
        )

    comments = Comment.objects.filter(post=post_id)
    post = Post.objects.get(id=post_id)

    context = {"post": post, "comments": comments}
    return render(request, "FeedApp/comments.html", context)
