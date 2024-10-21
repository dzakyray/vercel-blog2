from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Post URLs
    path('', views.post_list, name='post_list'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('category/<slug:slug>/', views.post_list_by_category, name='post_list_by_category'),
    path('tag/<slug:tag_slug>/', views.post_list_by_tag, name='post_list_by_tag'),
    path('author/<str:author_username>/', views.post_list_by_author, name='post_list_by_author'),
    path('date/<int:year>/<int:month>/<int:day>/', views.post_list_by_date, name='post_list_by_date'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.post_detail, name='post_detail'),
    
    # Profile and authentication URLs
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),  # URL untuk register
    path('login/', views.CustomLoginView.as_view(), name='login'),  # URL untuk login
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Password change/reset URLs
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]
