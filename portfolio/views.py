from django.views.generic import TemplateView
from django.views import View
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect, render
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
from datetime import datetime
from .forms import ContactForm


class HomePageView(TemplateView):
    template_name = "components/home.html"
    json_file_path = "projects.json"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with open(self.json_file_path, "r") as f:
            projects_data = json.load(f)
        # Limiting projects to display on the home page
        context["projectsData"] = projects_data[:2]
        return context


class ProjectListView(TemplateView):
    template_name = "pages/project.html"
    json_file_path = "projects.json"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with open(self.json_file_path, "r") as f:
            projects_data = json.load(f)
        # Limiting projects to display on the home page
        context["projectsData"] = projects_data
        return context


class ResumeView(TemplateView):
    template_name = "pages/resume.html"


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
                subject=f"Portifolio New Contact Form Submission from {name}",
                message=f"Name: {name}\nEmail: {email}\nMessage: {message}",
                from_email=email,
                recipient_list=["usanaphtal112@gmail.com"],
                fail_silently=False,
            )

            messages.success(request, "Your message has been sent successfully!")
            return redirect("contact_me_view")
        else:
            messages.error(
                request, "There was an error with your submission. Please try again."
            )

        return render(request, self.template_name, {"form": form})


class ProjectContactView(View):
    template_name = "pages/project.html"

    def get(self, request):
        form = ContactForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            # Extract form data
            project = form.cleaned_data.get("project", "Not specified")
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            # Construct email body
            email_body = (
                f"You have received a new contact form submission:\n\n"
                f"Project: {project}\n"
                f"Name: {name}\n"
                f"Email: {email}\n\n"
                f"Message:\n{message}"
            )

            try:
                # Send email
                send_mail(
                    subject=f"Contact Form Submission - {project}",
                    message=email_body,
                    from_email=email,
                    recipient_list=["usa.naphtal@gmail.com"],
                    fail_silently=False,
                )
                # Success message and redirect
                messages.success(request, "Your message has been sent successfully!")
                return redirect("project_work")
            except Exception as e:
                # Error message
                messages.error(
                    request, "Failed to send your message. Please try again."
                )

        else:
            # Form validation failed
            messages.error(
                request, "There was an error with your submission. Please try again."
            )

        # Re-render the page with the form and errors
        return render(request, self.template_name, {"form": form})


def send_telegram_message(message, user_info=None):
    """Send message to your Telegram"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    # Format the message nicely
    formatted_message = f"""
🔥 NEW MESSAGE FROM PORTFOLIO CHAT!

💬 Message: {message}
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 IP: {user_info.get('ip', 'Unknown') if user_info else 'Unknown'}
📱 User Agent: {user_info.get('user_agent', 'Unknown') if user_info else 'Unknown'}

---
Reply directly to this chat to respond!
    """

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    data = {"chat_id": chat_id, "text": formatted_message, "parse_mode": "HTML"}

    try:
        response = requests.post(url, data=data, timeout=10)
        return response.json()
    except Exception as e:
        return None


@csrf_exempt
@require_http_methods(["POST"])
def handle_chat_message(request):
    """Handle incoming chat messages"""
    try:
        data = json.loads(request.body)
        message = data.get("message", "").strip()

        if not message:
            return JsonResponse({"error": "Message is required"}, status=400)

        # Get user info for better tracking
        user_info = {
            "ip": get_client_ip(request),
            "user_agent": request.META.get("HTTP_USER_AGENT", "Unknown"),
        }

        # Send to Telegram
        telegram_response = send_telegram_message(message, user_info)

        # You can also send an email as backup
        send_email_notification(message, user_info)

        return JsonResponse(
            {
                "success": True,
                "bot_response": "Thanks for your message! I'll get back to you soon. You can also reach me directly at usanaphtal112@gmail.com",
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_client_ip(request):
    """Get the real IP address of the client"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def send_email_notification(message, user_info):
    """Send email notification as backup"""
    from django.core.mail import send_mail
    from django.conf import settings

    subject = "New Portfolio Chat Message"
    email_message = f"""
    New message from your portfolio:

    Message: {message}
    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    IP: {user_info.get('ip', 'Unknown')}
    User Agent: {user_info.get('user_agent', 'Unknown')}
    """

    try:
        send_mail(
            subject,
            email_message,
            settings.DEFAULT_FROM_EMAIL,
            fail_silently=True,
        )
    except Exception as e:
        pass
