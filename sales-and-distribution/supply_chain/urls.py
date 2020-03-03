from django.contrib import admin
from django.contrib.auth import views as auth_views
from users import views as user_views
from django.urls import path, include
from . import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/done', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
    path('register/', user_views.register, name='register'),
    path('transaction/', include('transaction.urls')),
    path('inventory/', include('inventory.urls')),
    path('users/Profile', user_views.profile, name='Profile'),
    path('users/roles', user_views.user_roles, name = 'user-roles'),
    path('roles/new', user_views.add_user_roles, name = 'add-user-roles'),
    path('roles/edit/<id>', user_views.edit_user_roles, name = 'edit-user-roles'),
    path('roles/delete/<id>', user_views.delete_user_roles, name = 'delete-user-roles'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
