"""
Frontend Views
Serve HTML templates for login, register, dashboard, and generate code pages
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


class GenerateCodeView(TemplateView):
    """Serve generate entry code page"""
    template_name = 'generate_code.html'


class ManageGoodsView(TemplateView):
    """Serve manage goods page"""
    template_name = 'manage_goods.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'manage_goods'
        return context
