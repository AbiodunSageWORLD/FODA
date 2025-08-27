from .models import Vendor

class VendorAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_id = request.session.get("user_id")
        request.vendor_user = None
        if user_id:
            try:
                request.vendor_user = Vendor.objects.get(id=user_id)
            except Vendor.DoesNotExist:
                pass
        return self.get_response(request)