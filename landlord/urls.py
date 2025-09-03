from django.urls import path
from .views import PropertyListCreateView, PropertyRetrieveUpdateView, RoomListCreateView, RoomDetailView, TenantRoomDetailView, TenantPaymentCreateView, TenantPaymentListView, LandlordPaymentListView, LandlordPaymentDetailView

urlpatterns = [
    path('properties/', PropertyListCreateView.as_view(),
         name='landlord-properties'),
    path('properties/<int:pk>/', PropertyRetrieveUpdateView.as_view(),
         name='landlord-property-detail'),
    path('rooms/', RoomListCreateView.as_view(), name='room-list-create'),
    path('rooms/<int:pk>/', RoomDetailView.as_view(), name='room-detail'),
    path('tenant/room/', TenantRoomDetailView.as_view(), name='tenant-room-detail'),
    path('tenant/payments/', TenantPaymentCreateView.as_view(), name='tenant-payment-create'),
    path('tenant/payments/list/', TenantPaymentListView.as_view(), name='tenant-payment-list'),
    path('payments/', LandlordPaymentListView.as_view(), name='landlord-payment-list'),
    path('payments/<int:pk>/', LandlordPaymentDetailView.as_view(), name='landlord-payment-detail'),
]
