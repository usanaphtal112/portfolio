from django.urls import path
from .views import HomePageView, ProjectListView, ResumeView

urlpatterns = [
    path("", HomePageView.as_view(), name="home_views"),
    path("work/", ProjectListView.as_view(), name="project_work"),
    path("resume/", ResumeView.as_view(), name="resume_view"),
]
