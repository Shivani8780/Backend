from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, FileResponse
from django.views import View
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import EBooklet, UserEBookletSelection
from .views_custom import log_request, log_error

import json

User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationView(View):
    def post(self, request):
        log_request(request)
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            phone_number = data.get('phone_number')
            memberID = data.get('memberID')
            ebooklet_ids = data.get('ebooklets', [])

            if not username or not password:
                return JsonResponse({'error': 'Username and password are required.'}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists.'}, status=400)

            user = User.objects.create_user(username=username, email=email, password=password)
            user.phone_number = phone_number
            user.memberID = memberID
            user.save()

            # Create UserEBookletSelection entries
            for ebooklet_id in ebooklet_ids:
                try:
                    ebooklet = EBooklet.objects.get(pk=ebooklet_id)
                    user_ebooklet_selection = UserEBookletSelection.objects.create(
                        user=user,
                        view_option='none'  # default or customize as needed
                    )
                    user_ebooklet_selection.ebooklet.set([ebooklet])
                except EBooklet.DoesNotExist:
                    continue

            return JsonResponse({'message': 'User registered successfully.'})
        except Exception as e:
            log_error(e)
            return JsonResponse({'error': str(e)}, status=500)

from rest_framework.authtoken.models import Token

@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(View):
    def post(self, request):
        log_request(request)
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                return JsonResponse({'message': 'Login successful.', 'token': token.key})
            else:
                return JsonResponse({'error': 'Invalid credentials.'}, status=401)
        except Exception as e:
            log_error(e)
            return JsonResponse({'error': str(e)}, status=500)

@login_required
def StaffUserListView(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to view this resource.")
    users = User.objects.all().values('id', 'username', 'email', 'is_staff')
    return JsonResponse(list(users), safe=False)

@method_decorator(csrf_exempt, name='dispatch')
class UserEBookletSelectionUpdateView(View):
    def post(self, request, pk):
        # Implement update logic for UserEBookletSelection here
        return JsonResponse({'message': 'Update endpoint not implemented yet.'})

from .utils import generate_pdf_page_images

@method_decorator(csrf_exempt, name='dispatch')
class EBookletUploadView(View):
    def post(self, request):
        # Implement ebooklet upload logic here
        # For example, handle file upload and save to EBooklet model
        try:
            pdf_file = request.FILES.get('pdf_file')
            name = request.POST.get('name', 'Untitled')
            if not pdf_file:
                return JsonResponse({'error': 'No PDF file uploaded.'}, status=400)

            ebooklet = EBooklet.objects.create(name=name, pdf_file=pdf_file)
            ebooklet.save()

            # Generate page images for the uploaded PDF
            generate_pdf_page_images(ebooklet)

            return JsonResponse({'message': 'EBooklet uploaded and processed successfully.', 'ebooklet_id': ebooklet.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def UserEBookletView(request):
    user = request.user
    selections = UserEBookletSelection.objects.filter(user=user, approved=True).select_related('user').prefetch_related('ebooklet')
    ebooklets_data = []
    for selection in selections:
        for ebooklet in selection.ebooklet.all():
            ebooklets_data.append({
                'id': ebooklet.id,
                'name': ebooklet.name,
                'view_option': selection.view_option,
                'approved': selection.approved,
            })
    return JsonResponse({'ebooklets': ebooklets_data})

def ebooklets_list_view(request):
    # Return list of all ebooklets
    ebooklets = EBooklet.objects.all().values('id', 'name')
    return JsonResponse(list(ebooklets), safe=False)

import logging

logger = logging.getLogger(__name__)

from django.http import FileResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

import os

import mimetypes
from django.http import Http404

@login_required
def ebooklet_pdf_view(request, ebooklet_id):
    user = request.user
    try:
        ebooklet = get_object_or_404(EBooklet, pk=ebooklet_id)

        # Check if user has approved selection for this ebooklet
        selections = UserEBookletSelection.objects.filter(user=user, ebooklet=ebooklet, approved=True)
        if not selections.exists():
            logger.error(f"User {user} does not have access to ebooklet {ebooklet_id}")
            return HttpResponseForbidden("You do not have access to this ebooklet.")

        # Check view_option for the selection
        selection = selections.first()
        if selection.view_option == 'none':
            logger.error(f"User {user} has no view access to ebooklet {ebooklet_id}")
            return HttpResponseForbidden("You do not have access to view this ebooklet.")
        elif selection.view_option == 'preview':
            # TODO: Implement preview logic, e.g., serve a preview PDF or partial content
            logger.error(f"Preview access not implemented for ebooklet {ebooklet_id}")
            return HttpResponseForbidden("Preview access not implemented yet.")
        elif selection.view_option == 'full':
            # Serve the full PDF file
            if not ebooklet.pdf_file:
                logger.error(f"EBooklet {ebooklet_id} has no PDF file.")
                return HttpResponseForbidden("PDF file not available.")
            try:
                file_path = ebooklet.pdf_file.path
                logger.debug(f"Attempting to open PDF file at path: {file_path}")
                if not os.access(file_path, os.R_OK):
                    logger.error(f"PDF file is not readable: {file_path}")
                    return JsonResponse({'error': 'PDF file is not readable.'}, status=403)
                if not os.path.exists(file_path):
                    logger.error(f"PDF file does not exist at path: {file_path}")
                    return JsonResponse({'error': 'PDF file not found on server.'}, status=404)
                # Additional debug info
                logger.debug(f"File size: {os.path.getsize(file_path)} bytes")
                content_type, encoding = mimetypes.guess_type(file_path)
                if not content_type:
                    content_type = 'application/octet-stream'
                response = FileResponse(open(file_path, 'rb'), content_type=content_type)
                response['Content-Disposition'] = f'inline; filename="{ebooklet.name}.pdf"'
                return response
            except Exception as e:
                logger.error(f"Error opening PDF file for ebooklet {ebooklet_id}: {e}", exc_info=True)
                return JsonResponse({'error': 'Error opening PDF file.'}, status=500)
        else:
            logger.error(f"Invalid access level {selection.view_option} for ebooklet {ebooklet_id}")
            return HttpResponseForbidden("Invalid access level.")
    except Exception as e:
        logger.error(f"Error serving ebooklet PDF: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error while fetching PDF.'}, status=500)

from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@login_required
@require_GET
def ebooklet_page_images_view(request, ebooklet_id):
    user = request.user
    try:
        ebooklet = get_object_or_404(EBooklet, pk=ebooklet_id)

        # Check if user has approved selection for this ebooklet
        selections = UserEBookletSelection.objects.filter(user=user, ebooklet=ebooklet, approved=True)
        if not selections.exists():
            return HttpResponseForbidden("You do not have access to this ebooklet.")

        # Check view_option for the selection
        selection = selections.first()
        if selection.view_option != 'full':
            return HttpResponseForbidden("You do not have full access to view this ebooklet.")

        # Construct URLs for pre-rendered page images
        media_url = settings.MEDIA_URL
        page_images_dir = os.path.join('ebooklet_pages', str(ebooklet.id))
        page_images_path = os.path.join(settings.MEDIA_ROOT, page_images_dir)

        import logging
        logger.debug(f"ebooklet_page_images_view: page_images_path={page_images_path}")
        if not os.path.exists(page_images_path):
            logger.error(f"Page images path does not exist: {page_images_path}")
            return JsonResponse({'error': 'Page images not found. Please upload and process the ebooklet again.'}, status=404)

        # List all page image files sorted by page number
        files = sorted(f for f in os.listdir(page_images_path) if f.endswith('.png'))
        logger.debug(f"Files found in page_images_path: {files}")
        page_urls = [request.build_absolute_uri(os.path.join(media_url, page_images_dir, f)) for f in files]

        return JsonResponse({'page_images': page_urls})
    except Exception as e:
        logger.error(f"Error serving ebooklet page images: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error while fetching page images.'}, status=500)

@login_required
@require_GET
def ebooklet_static_pdf_view(request, ebooklet_id):
    """
    Serve static PDF files with authentication and access control
    """
    user = request.user
    try:
        ebooklet = get_object_or_404(EBooklet, pk=ebooklet_id)

        # Check if user has approved selection for this ebooklet
        selections = UserEBookletSelection.objects.filter(user=user, ebooklet=ebooklet, approved=True)
        if not selections.exists():
            logger.error(f"User {user} does not have access to ebooklet {ebooklet_id}")
            return HttpResponseForbidden("You do not have access to this ebooklet.")

        # Check view_option for the selection
        selection = selections.first()
        if selection.view_option == 'none':
            logger.error(f"User {user} has no view access to ebooklet {ebooklet_id}")
            return HttpResponseForbidden("You do not have access to view this ebooklet.")
        elif selection.view_option == 'preview':
            # TODO: Implement preview logic, e.g., serve a preview PDF or partial content
            logger.error(f"Preview access not implemented for ebooklet {ebooklet_id}")
            return HttpResponseForbidden("Preview access not implemented yet.")
        elif selection.view_option == 'full':
            # Check if static_pdf_filename field exists (migration might not be run yet)
            static_filename = None
            try:
                # Check if the field exists in the model
                if hasattr(ebooklet, 'static_pdf_filename'):
                    static_filename = ebooklet.static_pdf_filename
                else:
                    logger.warning(f"static_pdf_filename field not found in model, falling back to dynamic serving")
                    return ebooklet_pdf_view(request, ebooklet_id)
            except Exception as field_error:
                logger.warning(f"Error accessing static_pdf_filename field: {field_error}, falling back to dynamic serving")
                return ebooklet_pdf_view(request, ebooklet_id)
            
            # Serve the static PDF file
            if not static_filename:
                # Fallback: try to determine filename from ebooklet name or use dynamic serving
                logger.warning(f"No static filename set for ebooklet {ebooklet_id}, falling back to dynamic serving")
                return ebooklet_pdf_view(request, ebooklet_id)
            
            # Check if static PDF file exists
            try:
                static_pdf_path = os.path.join(settings.BASE_DIR, 'static', 'pdfs', static_filename)
                if not os.path.exists(static_pdf_path):
                    logger.warning(f"Static PDF file not found: {static_pdf_path}, falling back to dynamic serving")
                    return ebooklet_pdf_view(request, ebooklet_id)
            except Exception as path_error:
                logger.warning(f"Error checking static PDF path: {path_error}, falling back to dynamic serving")
                return ebooklet_pdf_view(request, ebooklet_id)
            
            # Construct static PDF URL
            try:
                static_pdf_url = request.build_absolute_uri(f"{settings.STATIC_URL}pdfs/{static_filename}")
                logger.info(f"Serving static PDF for ebooklet {ebooklet_id}: {static_pdf_url}")
                
                # Return the static PDF URL as JSON response for frontend to handle
                return JsonResponse({
                    'pdf_url': static_pdf_url,
                    'filename': static_filename,
                    'ebooklet_name': ebooklet.name
                })
            except Exception as url_error:
                logger.warning(f"Error constructing static PDF URL: {url_error}, falling back to dynamic serving")
                return ebooklet_pdf_view(request, ebooklet_id)
        else:
            logger.error(f"Invalid access level {selection.view_option} for ebooklet {ebooklet_id}")
            return HttpResponseForbidden("Invalid access level.")
    except Exception as e:
        logger.error(f"Error serving static ebooklet PDF: {e}", exc_info=True)
        # Fallback to dynamic serving on any error
        logger.info(f"Falling back to dynamic serving for ebooklet {ebooklet_id}")
        try:
            return ebooklet_pdf_view(request, ebooklet_id)
        except Exception as fallback_error:
            logger.error(f"Fallback to dynamic serving also failed: {fallback_error}")
            return JsonResponse({'error': 'PDF serving temporarily unavailable'}, status=500)

@login_required
@require_GET
def debug_static_pdf_view(request, ebooklet_id):
    """
    Debug endpoint to test static PDF serving without authentication checks
    """
    try:
        ebooklet = get_object_or_404(EBooklet, pk=ebooklet_id)
        
        debug_info = {
            'ebooklet_id': ebooklet_id,
            'ebooklet_name': ebooklet.name,
            'has_static_field': hasattr(ebooklet, 'static_pdf_filename'),
            'static_filename': getattr(ebooklet, 'static_pdf_filename', None),
            'base_dir': str(settings.BASE_DIR),
            'static_root': str(settings.STATIC_ROOT),
            'static_url': settings.STATIC_URL,
        }
        
        # Check if static PDF file exists
        static_filename = getattr(ebooklet, 'static_pdf_filename', None)
        if static_filename:
            static_pdf_path = os.path.join(settings.BASE_DIR, 'static', 'pdfs', static_filename)
            collected_pdf_path = os.path.join(settings.STATIC_ROOT, 'pdfs', static_filename)
            
            debug_info.update({
                'source_path': static_pdf_path,
                'source_exists': os.path.exists(static_pdf_path),
                'collected_path': collected_pdf_path,
                'collected_exists': os.path.exists(collected_pdf_path),
                'static_url_full': request.build_absolute_uri(f"{settings.STATIC_URL}pdfs/{static_filename}")
            })
        
        return JsonResponse({'debug': debug_info})
        
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}", exc_info=True)
        return JsonResponse({'error': str(e), 'debug': {'ebooklet_id': ebooklet_id}}, status=500)

