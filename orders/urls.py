from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path('create/', views.order_create_view, name='order_create'),
    path("invoices/", views.my_invoices, name="my_invoices"),
    path("invoices/<int:invoice_id>/", views.invoice_detail, name="invoice_detail"),
    path('download_invoice/<int:order_id>/', views.download_invoice_pdf, name='download_invoice'),
]
