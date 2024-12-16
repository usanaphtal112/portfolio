from django.urls import path
from .views import (
    HomePageView,
    ProjectListView,
    ResumeView,
    ContactMeView,
    ProjectContactView,
)

urlpatterns = [
    path("", HomePageView.as_view(), name="home_views"),
    path("work/", ProjectListView.as_view(), name="project_work"),
    path("resume/", ResumeView.as_view(), name="resume_view"),
    path("contact/me/", ContactMeView.as_view(), name="contact_me_view"),
    path("project/contact/", ProjectContactView.as_view(), name="project_contact_me"),
]
