import logging
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

class MyView(APIView):
    def get(self, request):
        logger.debug("Debug message: This will only show in DEBUG mode")
        logger.info("Info: User %s accessed the homepage", request.user.username)
        logger.warning("Warning: Something suspicious happened")
        
        try:
            # Simulate an error
            1 / 0
        except Exception as e:
            logger.error("Error occurred in MyView.get()", exc_info=True)
            logger.exception("This also logs the full traceback")  # Same as above but cleaner

        return Response("Hello, logging world!")
