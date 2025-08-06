from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import FileResponse
import os
import mimetypes
import logging
from .models import EBooklet, UserEBookletSelection

logger = logging.getLogger(__name__)

@login_required
def ebooklet_dynamic_pdf_view(request, ebooklet_id):
    """
    Generate and serve dynamic PDF files with proper error handling
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
            # TODO: Implement preview logic
            logger.error(f"Preview access not implemented for ebooklet {ebooklet_id}")
            return HttpResponseForbidden("Preview access not implemented yet.")
        elif selection.view_option == 'full':
            # Generate dynamic PDF
            if not ebooklet.pdf_file:
                logger.error(f"EBooklet {ebooklet_id} has no PDF file.")
                return HttpResponseForbidden("PDF file not available.")

            try:
                file_path = ebooklet.pdf_file.path
                logger.debug(f"Attempting to open PDF file at path: {file_path}")
                
                if not os.path.exists(file_path):
                    logger.error(f"PDF file does not exist: {file_path}")
                    return JsonResponse({'error': 'PDF file not found'}, status=404)

                if not os.access(file_path, os.R_OK):
                    logger.error(f"PDF file is not readable: {file_path}")
                    return JsonResponse({'error': 'PDF file is not readable'}, status=403)

                # Serve the PDF file
                content_type, encoding = mimetypes.guess_type(file_path)
                if not content_type:
                    content_type = 'application/pdf'
                
                response = FileResponse(open(file_path, 'rb'), content_type=content_type)
                response['Content-Disposition'] = f'inline; filename="{ebooklet.name}.pdf"'
                return response
                
            except Exception as e:
                logger.error(f"Error serving dynamic PDF for ebooklet {ebooklet_id}: {e}", exc_info=True)
                return JsonResponse({'error': 'Error generating PDF'}, status=500)
        else:
            logger.error(f"Invalid access level {selection.view_option} for ebooklet {ebooklet_id}")
            return HttpResponseForbidden("Invalid access level.")
            
    except Exception as e:
        logger.error(f"Error serving dynamic ebooklet PDF: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)
