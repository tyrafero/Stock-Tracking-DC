from django.views.generic import View
from django.http import HttpResponse, Http404
from django.conf import settings
import os


class ReactAppView(View):
    """
    Serves the React application's index.html file for all non-API routes.
    This allows React Router to handle client-side routing.
    """
    def get(self, request, *args, **kwargs):
        try:
            # Path to the React build's index.html
            index_path = os.path.join(settings.REACT_BUILD_DIR, 'index.html')

            if not os.path.exists(index_path):
                raise Http404("React app not found. Please build the frontend first.")

            with open(index_path, 'r', encoding='utf-8') as f:
                return HttpResponse(f.read(), content_type='text/html')
        except FileNotFoundError:
            raise Http404("React app not found. Please build the frontend first.")
