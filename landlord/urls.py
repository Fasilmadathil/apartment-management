from django.urls import path
from .views import PropertyListCreateView, PropertyRetrieveUpdateView, RoomListCreateView, RoomDetailView

urlpatterns = [
    path('properties/', PropertyListCreateView.as_view(),
         name='landlord-properties'),
    path('properties/<int:pk>/', PropertyRetrieveUpdateView.as_view(),
         name='landlord-property-detail'),
    path('rooms/', RoomListCreateView.as_view(), name='room-list-create'),
    path('rooms/<int:pk>/', RoomDetailView.as_view(), name='room-detail'),
]
