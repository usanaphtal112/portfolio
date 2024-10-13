from django.views.generic import TemplateView
import json


class HomePageView(TemplateView):
    template_name = "components/home.html"
    json_file_path = "projects.json"  # Adjust path as per your project structure

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with open(self.json_file_path, "r") as f:
            projects_data = json.load(f)
        # Limiting projects to display on the home page
        context["projectsData"] = projects_data[:2]  # Displaying first two projects
        return context


class ProjectListView(TemplateView):
    template_name = "pages/project.html"
    json_file_path = "projects.json"  # Adjust path as per your project structure

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with open(self.json_file_path, "r") as f:
            projects_data = json.load(f)
        # Limiting projects to display on the home page
        context["projectsData"] = projects_data
        return context


class ResumeView(TemplateView):
    template_name = "pages/resume_html.html"
