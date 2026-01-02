"""
Health check endpoint for Docker and monitoring systems
"""
from django.db import connection
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import datetime


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint that verifies:
    - API is responding
    - Database connection is working
    - Redis/cache is working

    Returns 200 OK if all systems are operational
    Returns 503 Service Unavailable if any system is down
    """
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'checks': {}
    }

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = f'error: {str(e)}'

    # Check cache/Redis connection
    try:
        cache_key = 'health_check_test'
        cache.set(cache_key, 'test', 10)
        cache_value = cache.get(cache_key)
        if cache_value == 'test':
            health_status['checks']['cache'] = 'ok'
        else:
            health_status['checks']['cache'] = 'error: cache read/write failed'
            health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['cache'] = f'error: {str(e)}'

    # Determine HTTP status code
    if health_status['status'] == 'healthy':
        return Response(health_status, status=status.HTTP_200_OK)
    else:
        return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)
