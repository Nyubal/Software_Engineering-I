from django.contrib import admin
from django.urls import path
from authentication.views import register_view, login_view, budget_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('budget/', budget_view, name='budget_config'),
]
