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


class CreateOrderView(TemplateView):
    """Serve create order page"""
    template_name = 'create_order.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'create_order'
        return context


class CheckoutView(TemplateView):
    """Serve checkout page"""
    template_name = 'checkout.html'


class PaymentView(TemplateView):
    """Serve payment page"""
    template_name = 'payment.html'


class PaymentResultView(TemplateView):
    """Serve payment result page"""
    template_name = 'payment_result.html'


class ViewOrdersView(TemplateView):
    """Serve view orders page"""
    template_name = 'view_orders.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'view_orders'
        return context


class ManageMerchantsView(TemplateView):
    """Serve manage merchants page"""
    template_name = 'manage_merchants.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'manage_merchants'
        return context
