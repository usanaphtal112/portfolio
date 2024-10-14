from django.views.generic import TemplateView
from django.views import View
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import ContactForm
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


class ContactMeView(View):
    template_name = "pages/contactme.html"

    def get(self, request):
        form = ContactForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data.get("email", "")
            message = form.cleaned_data["message"]

            # Send email
            send_mail(
                subject=f"New contact form submission from {name}",
                message=f"Name: {name}\nEmail: {email}\nMessage: {message}",
                from_email=email,
                recipient_list=["usa.naphtal@gmail.com"],  # Replace with your email
                fail_silently=False,
            )

            messages.success(request, "Your message has been sent successfully!")
            return redirect("contact_me_view")  # Adjust this to match your URL name
        else:
            messages.error(
                request, "There was an error with your submission. Please try again."
            )

        return render(request, self.template_name, {"form": form})
