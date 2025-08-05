import logging

logger = logging.getLogger(__name__)

def log_request(request):
    logger.info(f"Request method: {request.method}, path: {request.get_full_path()}, user: {request.user}")

def log_error(error):
    logger.error(f"Error: {error}", exc_info=True)
