from django.contrib.auth.middleware import PersistentRemoteUserMiddleware

class CustomHeaderMiddleware(PersistentRemoteUserMiddleware):
    header = 'HTTP_CAS_USER'