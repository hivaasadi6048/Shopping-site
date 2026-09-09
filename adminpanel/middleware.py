import datetime
import logging
from django.conf import settings
from django.contrib import auth
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse, NoReverseMatch

logger = logging.getLogger(__name__)

class AutoLogoutMiddleware(MiddlewareMixin):
    """
    خروج خودکار کاربر بعد از مدت مشخصی از عدم فعالیت (inactivity)
    - مسیرهای پرداخت و فاکتور مستثنا هستند.
    - با timezone سازگار است.
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.exempt_urls = self._build_exempt_urls()

    def _build_exempt_urls(self):
        """مسیرهای مستثنا از بررسی خروج خودکار"""
        urls = ['/admin/login/']
        try:
            urls.append(reverse('payment:payment_callback'))
        except NoReverseMatch:
            urls.append('/payment/callback/')
        try:
            urls.append(reverse('payment:payment_process'))
        except NoReverseMatch:
            urls.append('/payment/process/')
        urls.append('/order/invoices/')
        return urls

    def process_request(self, request):
        # اگر کاربر لاگین نکرده، نیازی به بررسی نیست
        if not request.user.is_authenticated:
            return

        path = request.path or '/'
        # مسیرهای مستثنا مثل پرداخت و فاکتورها
        if any(path.startswith(u) for u in self.exempt_urls):
            request.session['last_activity'] = timezone.now().isoformat()
            request.session.modified = True
            return

        now = timezone.now()
        last_activity_str = request.session.get('last_activity')

        try:
            if last_activity_str:
                last_activity = datetime.datetime.fromisoformat(last_activity_str)
                if timezone.is_naive(last_activity):
                    last_activity = timezone.make_aware(last_activity, timezone.get_current_timezone())

                elapsed = (now - last_activity).total_seconds()
                # اگر زمان inactivity از حد مجاز بیشتر بود → logout
                if elapsed > settings.SESSION_COOKIE_AGE:
                    logger.info(f"[AutoLogout] user={request.user} inactive={elapsed:.0f}s -> logout")
                    auth.logout(request)
                    request.session.flush()
                    return
        except Exception as e:
            logger.warning(f"[AutoLogout] error processing session: {e}")

        # در هر درخواست، زمان فعلی را به‌عنوان آخرین فعالیت ذخیره کن
        request.session['last_activity'] = now.isoformat()
        request.session.modified = True
