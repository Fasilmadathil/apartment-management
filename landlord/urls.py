from django.urls import path
from .views import PropertyListCreateView, PropertyRetrieveUpdateView, RoomListCreateView, RoomDetailView, TenantRoomDetailView, TenantPaymentCreateView, TenantPaymentListView, LandlordPaymentListView, LandlordPaymentDetailView, AssignTenantView, ElectricityBillCreateView, TenantElectricityBillListView, CommunityMessageCreateView, CommunityMessageListView, LandlordContactView, ChatView, IncomeAnalyticsView

urlpatterns = [
    path('properties/', PropertyListCreateView.as_view(),
         name='landlord-properties'),
    path('properties/<int:pk>/', PropertyRetrieveUpdateView.as_view(),
         name='landlord-property-detail'),
    path('rooms/', RoomListCreateView.as_view(), name='room-list-create'),
    path('rooms/<int:pk>/', RoomDetailView.as_view(), name='room-detail'),
    path('assign-tenant/', AssignTenantView.as_view(), name='assign-tenant'),
    path('tenant/room/', TenantRoomDetailView.as_view(), name='tenant-room-detail'),
    path('tenant/payments/', TenantPaymentCreateView.as_view(), name='tenant-payment-create'),
    path('tenant/payments/list/', TenantPaymentListView.as_view(), name='tenant-payment-list'),
    path('payments/', LandlordPaymentListView.as_view(), name='landlord-payment-list'),
    path('payments/<int:pk>/', LandlordPaymentDetailView.as_view(), name='landlord-payment-detail'),
    
    # Electricity
    path('electricity/add/', ElectricityBillCreateView.as_view(), name='electricity-bill-create'),
    path('tenant/electricity/', TenantElectricityBillListView.as_view(), name='tenant-electricity-list'),

    # Community
    path('community/add/', CommunityMessageCreateView.as_view(), name='community-message-create'),
    path('community/', CommunityMessageListView.as_view(), name='community-message-list'),

    # Contact
    path('tenant/contact/', LandlordContactView.as_view(), name='tenant-landlord-contact'),

    # Chat
    path('chat/', ChatView.as_view(), name='chat'),




    # Analytics
    path('analytics/income/', IncomeAnalyticsView.as_view(), name='income-analytics'),
]
