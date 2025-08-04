from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    StaffUserListView,
    UserEBookletSelectionUpdateView,
    EBookletUploadView,
    UserEBookletView,
    ebooklet_pdf_view,
    ebooklet_page_images_view,
    ebooklets_list_view,
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('staff/users/', StaffUserListView, name='staff-user-list'),
    path('user/ebooklet/', UserEBookletView, name='user-ebooklet'),
    path('staff/ebooklet/upload/', EBookletUploadView.as_view(), name='ebooklet-upload'),
    path('staff/ebooklet-selection/<int:pk>/', UserEBookletSelectionUpdateView.as_view(), name='ebooklet-selection-update'),
    path('ebooklet/<int:ebooklet_id>/pdf/', ebooklet_pdf_view, name='ebooklet-pdf-view'),
    path('ebooklet/<int:ebooklet_id>/page-images/', ebooklet_page_images_view, name='ebooklet-page-images'),
    path('ebooklet/<int:ebooklet_id>/pdf-file/', ebooklet_pdf_view, name='ebooklet-pdf-file'),
    path('ebooklets/', ebooklets_list_view, name='ebooklets-list'),
]
