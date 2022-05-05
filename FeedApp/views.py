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
    profile = Profile.objects.filter(
        user=request.user
    )  # can't use get() bc doesnt work with exists
    if not profile.exists():
        Profile.objects.create(user=request.user)
    # now that we know they have a profile we can get them
    profile = Profile.objects.get(user=request.user)
