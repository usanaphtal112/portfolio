from django.urls import path
from .views import (
    HomePageView,
    ProjectListView,
    ResumeView,
    ContactMeView,
    ProjectContactView,
    handle_chat_message,
    reply_chat_view,
    handle_reply_message,
    check_reply_status,
    close_reply_session,
)

urlpatterns = [
    path("", HomePageView.as_view(), name="home_views"),
    path("work/", ProjectListView.as_view(), name="project_work"),
    path("resume/", ResumeView.as_view(), name="resume_view"),
    path("contact/me/", ContactMeView.as_view(), name="contact_me_view"),
    path("project/contact/", ProjectContactView.as_view(), name="project_contact_me"),
    path("api/chat/", handle_chat_message, name="handle_chat_message"),
    path("chat/reply/<str:token>/", reply_chat_view, name="reply_chat"),
    path(
        "api/chat/reply/<str:token>/", handle_reply_message, name="handle_reply_message"
    ),
    path("api/chat/check-reply/", check_reply_status, name="check_reply_status"),
    path(
        "api/chat/close/<str:token>/", close_reply_session, name="close_reply_session"
    ),
]
