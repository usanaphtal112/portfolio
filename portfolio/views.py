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
import uuid
import json
from datetime import datetime, timedelta
from .forms import ContactForm

ACTIVE_REPLY_SESSIONS = {}


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


# class ResumeView(TemplateView):
#     template_name = "pages/resume.html"


from django.http import FileResponse
import os


class ResumeView(View):
    def get(self, request, *args, **kwargs):
        # Locate the file
        file_path = os.path.join(settings.BASE_DIR, "static", "documents", "resume.pdf")

        # Open as binary and return as FileResponse
        response = FileResponse(open(file_path, "rb"), content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="resume.pdf"'
        return response


class AboutMeView(TemplateView):
    template_name = "pages/aboutme.html"


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


def generate_reply_token():
    """Generate a unique reply token"""
    return str(uuid.uuid4())


def create_reply_session(original_message, user_info):
    """Create a temporary reply session"""
    token = generate_reply_token()
    session_data = {
        "original_message": original_message,
        "user_info": user_info,
        "created_at": datetime.now(),
        "messages": [],  # Store conversation history
        "active": True,
    }
    ACTIVE_REPLY_SESSIONS[token] = session_data
    return token


def cleanup_expired_sessions():
    """Clean up expired sessions (older than 24 hours)"""
    current_time = datetime.now()
    expired_tokens = []

    for token, session in ACTIVE_REPLY_SESSIONS.items():
        if current_time - session["created_at"] > timedelta(hours=24):
            expired_tokens.append(token)

    for token in expired_tokens:
        del ACTIVE_REPLY_SESSIONS[token]


def send_telegram_message(message, user_info=None, reply_token=None):
    """Send message to your Telegram with reply link"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    # Create reply URL if token is provided
    reply_url = ""
    if reply_token:
        base_url = getattr(settings, "BASE_URL", "http://localhost:8000")
        reply_url = f"{base_url}/chat/reply/{reply_token}/"

    # Format the message nicely
    formatted_message = f"""
🔥 NEW MESSAGE FROM PORTFOLIO CHAT!

💬 Message: {message}
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 IP: {user_info.get('ip', 'Unknown') if user_info else 'Unknown'}
📱 User Agent: {user_info.get('user_agent', 'Unknown') if user_info else 'Unknown'}

---
{f'🔗 Reply Link: {reply_url}' if reply_url else 'Reply directly to this chat to respond!'}
⏰ Link expires in 24 hours
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

        # Clean up expired sessions
        cleanup_expired_sessions()

        # Get user info for better tracking
        user_info = {
            "ip": get_client_ip(request),
            "user_agent": request.META.get("HTTP_USER_AGENT", "Unknown"),
        }

        # Create reply session
        reply_token = create_reply_session(message, user_info)

        # Send to Telegram with reply link
        telegram_response = send_telegram_message(message, user_info, reply_token)

        # You can also send an email as backup
        # send_email_notification(message, user_info, reply_token)

        return JsonResponse(
            {
                "success": True,
                "bot_response": "Thanks for your message! I'll get back to you soon. You can also reach me directly at usanaphtal112@gmail.com",
                "reply_token": reply_token,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def reply_chat_view(request, token):
    """Handle reply chat interface"""
    cleanup_expired_sessions()

    # Check if token exists and is valid
    if token not in ACTIVE_REPLY_SESSIONS:
        return render(request, "chats/reply_expired.html")

    session_data = ACTIVE_REPLY_SESSIONS[token]

    # Check if session is still active
    if not session_data.get("active", False):
        return render(request, "chats/reply_expired.html")

    context = {
        "token": token,
        "original_message": session_data["original_message"],
        "user_info": session_data["user_info"],
        "messages": session_data["messages"],
        "created_at": session_data["created_at"],
    }

    return render(request, "chats/reply_chat.html", context)


@csrf_exempt
@require_http_methods(["POST"])
def handle_reply_message(request, token):
    """Handle reply messages from you"""
    try:
        cleanup_expired_sessions()

        # Check if token exists and is valid
        if token not in ACTIVE_REPLY_SESSIONS:
            return JsonResponse({"error": "Session expired or invalid"}, status=400)

        session_data = ACTIVE_REPLY_SESSIONS[token]

        if not session_data.get("active", False):
            return JsonResponse({"error": "Session expired"}, status=400)

        data = json.loads(request.body)
        reply_message = data.get("message", "").strip()

        if not reply_message:
            return JsonResponse({"error": "Message is required"}, status=400)

        # Add your reply to the conversation
        message_data = {
            "sender": "admin",
            "message": reply_message,
            "timestamp": datetime.now().isoformat(),
        }
        session_data["messages"].append(message_data)

        # Store the reply in the shared session dict for user polling
        session_data["pending_reply"] = {
            "reply": reply_message,
            "timestamp": datetime.now().isoformat(),
        }

        return JsonResponse({"success": True, "message": "Reply sent successfully!"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def check_reply_status(request):
    """Check if there's a reply for the user"""
    try:
        data = json.loads(request.body)
        token = data.get("token")

        if not token:
            return JsonResponse({"has_reply": False})

        # Check if there's a pending reply in the shared session dict
        if token in ACTIVE_REPLY_SESSIONS:
            session_data = ACTIVE_REPLY_SESSIONS[token]
            pending_reply = session_data.get("pending_reply")
            if pending_reply:
                # Remove after delivering
                reply_text = pending_reply["reply"]
                del session_data["pending_reply"]
                return JsonResponse(
                    {
                        "has_reply": True,
                        "reply": pending_reply["reply"],
                        "timestamp": pending_reply["timestamp"],
                    }
                )

        return JsonResponse({"has_reply": False})

    except Exception as e:
        return JsonResponse({"has_reply": False})


def close_reply_session(request, token):
    """Close a reply session"""
    if token in ACTIVE_REPLY_SESSIONS:
        ACTIVE_REPLY_SESSIONS[token]["active"] = False

    return JsonResponse({"success": True, "message": "Session closed"})


def get_client_ip(request):
    """Get the real IP address of the client"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


# def send_email_notification(message, user_info, reply_token=None):
#     """Send email notification as backup"""
#     from django.core.mail import send_mail
#     from django.conf import settings

#     reply_url = ""
#     if reply_token:
#         base_url = getattr(settings, "BASE_URL", "http://localhost:8000")
#         reply_url = f"{base_url}/chat/reply/{reply_token}/"

#     subject = "New Portfolio Chat Message"
#     email_message = f"""
#     New message from your portfolio:

#     Message: {message}
#     Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
#     IP: {user_info.get('ip', 'Unknown')}
#     User Agent: {user_info.get('user_agent', 'Unknown')}

#     {f'Reply Link: {reply_url}' if reply_url else ''}
#     """

#     try:
#         send_mail(
#             subject,
#             email_message,
#             settings.DEFAULT_FROM_EMAIL,
#             [settings.DEFAULT_FROM_EMAIL],  # Send to yourself
#             fail_silently=True,
#         )
#     except Exception as e:
#         pass
