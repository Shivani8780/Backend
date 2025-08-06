from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    StaffUserListView,
    UserEBookletSelectionUpdateView,
    EBookletUploadView,
    UserEBookletView,
    ebooklet_pdf_view,
    ebooklet_static_pdf_view,
    ebooklet_page_images_view,
    ebooklets_list_view,
    debug_static_pdf_view,
    ebooklet_static_pdf_direct_view,
)
from .views_dynamic_pdf import ebooklet_dynamic_pdf_view

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('staff/users/', StaffUserListView, name='staff-user-list'),
    path('user/ebooklet/', UserEBookletView, name='user-ebooklet'),
    path('staff/ebooklet/upload/', EBookletUploadView.as_view(), name='ebooklet-upload'),
    path('staff/ebooklet-selection/<int:pk>/', UserEBookletSelectionUpdateView.as_view(), name='ebooklet-selection-update'),
    
    # Static PDF endpoints
    path('ebooklet/<int:ebooklet_id>/pdf-static/', ebooklet_static_pdf_direct_view, name='ebooklet-pdf-static'),
    path('ebooklet/<int:ebooklet_id>/pdf-dynamic/', ebooklet_dynamic_pdf_view, name='ebooklet-pdf-dynamic'),
    path('ebooklet/<int:ebooklet_id>/pdf-debug/', debug_static_pdf_view, name='ebooklet-pdf-debug'),
    path('ebooklet/<int:ebooklet_id>/page-images/', ebooklet_page_images_view, name='ebooklet-page-images'),
    
    # Legacy endpoints (for backward compatibility)
    path('ebooklet/<int:ebooklet_id>/pdf/', ebooklet_pdf_view, name='ebooklet-pdf-view'),
    path('ebooklet/<int:ebooklet_id>/pdf-file/', ebooklet_pdf_view, name='ebooklet-pdf-file'),
    
    # Utility endpoints
    path('ebooklets/', ebooklets_list_view, name='ebooklets-list'),
]
