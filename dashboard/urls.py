from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('',  views.dashboard, name='dashboard'),
    path("profile/", views.profile_view, name="profile"),
    path("addresses/", views.address_list_view, name="address_list"),
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("change-password/", views.change_password_view, name="change_password"),
    path("logout/", views.logout_view, name="logout"),
    path("addresses/delete/<int:pk>/",views.delete_address_view, name="delete_address"),

]


