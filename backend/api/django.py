import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wealthwise.settings")

# Setup Django
import django
django.setup()

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()


def handler(request, response):
    """Handler for Vercel serverless functions."""
    # Convert Vercel request to WSGI environ
    import io
    from urllib.parse import unquote, quote, urlparse, parse_qs

    environ = {
        "REQUEST_METHOD": request.method,
        "SCRIPT_NAME": "",
        "PATH_INFO": unquote(request.path) or "/",
        "QUERY_STRING": request.query_string or "",
        "CONTENT_TYPE": request.headers.get("content-type", ""),
        "CONTENT_LENGTH": request.headers.get("content-length", ""),
        "SERVER_NAME": request.headers.get("host", "localhost").split(":")[0],
        "SERVER_PORT": request.headers.get("host", "localhost").split(":")[-1] if ":" in request.headers.get("host", "") else "443",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "https",
        "wsgi.input": io.BytesIO(request.body if request.body else b""),
        "wsgi.errors": sys.stderr,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
    }

    # Add HTTP headers
    for key, value in request.headers.items():
        key = key.upper().replace("-", "_")
        if key not in ("CONTENT_TYPE", "CONTENT_LENGTH"):
            key = f"HTTP_{key}"
        environ[key] = value

    # Call the WSGI application
    response_data = []
    status = None
    response_headers = []

    def start_response(status_str, headers):
        nonlocal status, response_headers
        status = int(status_str.split()[0])
        response_headers = headers
        return response_data.append

    app_iter = application(environ, start_response)
    try:
        response_data.extend(app_iter)
    finally:
        if hasattr(app_iter, "close"):
            app_iter.close()

    # Build Vercel response
    body = b"".join(response_data)
    headers = {key: value for key, value in response_headers}

    return {
        "statusCode": status or 200,
        "headers": headers,
        "body": body.decode("utf-8") if isinstance(body, bytes) else body,
        "isBase64Encoded": False,
    }
