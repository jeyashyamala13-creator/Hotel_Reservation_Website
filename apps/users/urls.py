from django.urls import path
from .views import RegisterView, logout_user
# Import-ai sariyaana folder path-la kudunga
# Since they are in the same folder, use:
from .views import RoleBasedLoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    # 'login/' nu oru path mattum thaan irukkanum
    path('login/', RoleBasedLoginView.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
]