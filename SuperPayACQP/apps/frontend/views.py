"""
Frontend Views
Serve HTML templates for login, register, and dashboard pages
"""
from django.views.generic import TemplateView


class LoginView(TemplateView):
    """Serve login page"""
    template_name = 'login.html'


class RegisterView(TemplateView):
    """Serve register page"""
    template_name = 'register.html'


class DashboardView(TemplateView):
    """Serve dashboard page"""
    template_name = 'dashboard.html'
