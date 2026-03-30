"""
Frontend Views
Serve HTML templates for login, register, dashboard, and generate code pages
"""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class LoginView(TemplateView):
    """Serve login page"""
    template_name = 'login.html'


class RegisterView(TemplateView):
    """Serve register page"""
    template_name = 'register.html'


class DashboardView(LoginRequiredMixin, TemplateView):
    """Serve dashboard page"""
    template_name = 'dashboard.html'
    login_url = '/login'


class GenerateCodeView(LoginRequiredMixin, TemplateView):
    """Serve generate entry code page"""
    template_name = 'generate_code.html'
    login_url = '/login'


class ManageGoodsView(LoginRequiredMixin, TemplateView):
    """Serve manage goods page"""
    template_name = 'manage_goods.html'
    login_url = '/login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'manage_goods'
        return context


class CreateOrderView(LoginRequiredMixin, TemplateView):
    """Serve create order page"""
    template_name = 'create_order.html'
    login_url = '/login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'create_order'
        return context


class CheckoutView(LoginRequiredMixin, TemplateView):
    """Serve checkout page"""
    template_name = 'checkout.html'
    login_url = '/login'


class PaymentView(LoginRequiredMixin, TemplateView):
    """Serve payment page"""
    template_name = 'payment.html'
    login_url = '/login'


class PaymentResultView(LoginRequiredMixin, TemplateView):
    """Serve payment result page"""
    template_name = 'payment_result.html'
    login_url = '/login'


class ViewOrdersView(LoginRequiredMixin, TemplateView):
    """Serve view orders page"""
    template_name = 'view_orders.html'
    login_url = '/login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'view_orders'
        return context


class ManageMerchantsView(LoginRequiredMixin, TemplateView):
    """Serve manage merchants page"""
    template_name = 'manage_merchants.html'
    login_url = '/login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'manage_merchants'
        return context
