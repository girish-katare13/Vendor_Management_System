from django.urls import path
from .views import VendorListView,VendorDetailView,PurchaseOrderListView,PurchaseOrderDetailView,VendorPerformanceView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/vendors/', VendorListView.as_view(), name='vendor-list'),
    path('api/vendors/<int:pk>/', VendorDetailView.as_view(), name='vendor-detail'),

    path('api/purchase_orders/', PurchaseOrderListView.as_view(), name='purchase-order-list'),
    path('api/purchase_orders/<int:pk>/', PurchaseOrderDetailView.as_view(), name='purchase-order-detail'),

    path('api/vendors/<int:pk>/performance/', VendorPerformanceView.as_view(), name='vendor-performance'),
    path('api/token/', obtain_auth_token, name='api_token'),
]
