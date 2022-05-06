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


@login_required
def friendsfeed(request):
    comment_count_list = []
    like_count_list = []
    # grab all posts for this user by filtering username and sort by newest post
    friends = Profile.objects.filter(user=request.user).values("friends")
    posts = Post.objects.filter(username__in=friends).order_by("-date_posted")
    # get like and comments for each post
    for p in posts:
        c_count = Comment.objects.filter(post=p).count()
        l_count = Like.objects.filter(post=p).count()
        comment_count_list.append(c_count)
        like_count_list.append(l_count)

    # zip all info together for easier passing to context
    zipped_list = zip(posts, comment_count_list, like_count_list)

    # was like button pressed
    if request.method == "POST" and request.POST.get("like"):
        post_to_like = request.POST.get("like")
        # can only like a post one time
        like_already_exist = Like.objects.filter(
            post_id=post_to_like, username=request.user
        )
        if not like_already_exist():
            Like.objects.create(post_id=post_to_like, username=request.user)
            return redirect("FeedApp:friendsfeed")

    context = {"posts": posts, "zipped_list": zipped_list}
    return render(request, "FeedApp/friendsfeed.html", context)


# handle friend requests
@login_required
def friends(request):
    # admin profile and user profile
    admin_profile = Profile.objects.get(user=1)
    user_profile = Profile.objects.get(user=request.user)

    # get a list of user friends
    user_friends = user_profile.friends.all()
    user_friends_profiles = Profile.objects.filter(user__in=user_friends)

    # list of sent friend requests
    user_relationships = Relationship.objects.filter(sender=user_profile)
    request_sent_profiles = user_relationships.values("receiver")

    # list of who we can send a friend request to - everyone in system that is not a friend or hasn't been sent one already
    all_profiles = (
        Profile.objects.exclude(user=request.user)
        .exclude(id__in=user_friends_profiles)
        .exclude(id__in=request_sent_profiles)
    )

    # get friend requests received
    request_received_profiles = Relationship.objects.filter(
        receiver=user_profile, status="sent"
    )

    # create relationship with admin when user first joins so admin is friends with everyone
    if not user_relationships.exists():
        Relationship.objects.create(
            sender=user_profile, receiver=admin_profile, status="sent"
        )

    # which submit button was pressed - send or accept
    # all send requests
    if request.method == "POST" and request.POST.get("send_requests"):
        receivers = request.POST.getlist("send_requests")
        for receiver in receivers:
            receiver_profile = Profile.objects.get(id=receiver)
            Relationship.objects.create(
                sender=user_profile, receiver=receiver_profile, status="sent"
            )
        return redirect("FeedApp:friends")

    # all requests received
    if request.method == "POST" and request.POST.get("receive_requests"):
        senders = request.POST.getlist("receive_requests")
        for sender in senders:
            # update relationship model for the sender to status "accepted"
            Relationship.objects.filter(id=sender).update(status="accepted")

            # create relationship object to access the sender's user id
            # add that user id to the friends list of the user
            relationship_obj = Relationship.objects.get(id=sender)
            user_profile.friends.add(relationship_obj.sender.user)

            # add user to the friends list of sender profile
            relationship_obj.sender.friends.add(request.user)
        return redirect("FeedApp:friends")

    context = {
        "user_friends_profiles": user_friends_profiles,
        "user_relationships": user_relationships,
        "all_profiles": all_profiles,
        "request_received_profiles": request_received_profiles,
    }

    return render(request, "FeedApp/friends.html", context)
