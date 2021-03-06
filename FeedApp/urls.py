from django.urls import path
from . import views

app_name = "FeedApp"

urlpatterns = [
    path("", views.index, name="index"),
    # user can add and edit profile info
    path("profile/", views.profile, name="profile"),
    path("myfeed/", views.myfeed, name="myfeed"),
    path("new_post/", views.new_post, name="new_post"),
    path("comments/<int:postid>/", views.new_comment, name="comments"),
    path("friendsfeed/", views.friendsfeed, name="friendsfeed"),
    path("friends/", views.friends, name="friends"),
]
