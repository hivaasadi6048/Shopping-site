# adminpanel/utils.py
from .models import AuditLog

def create_audit_log(request, action, obj, extra_info=None):
    data_snapshot = {}
    try:
        # فقط فیلدهای متنی و عددی ساده رو ذخیره کن
        for field in obj._meta.fields:
            value = getattr(obj, field.name)
            if isinstance(value, (str, int, float, bool)) and field.name not in ['password']:
                data_snapshot[field.name] = value
    except Exception:
        data_snapshot = {}

    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')).split(',')[0].strip()
    ua = request.META.get('HTTP_USER_AGENT', 'unknown')    


    AuditLog.objects.create(
        user=request.user,
        action=action,
        model_name=obj._meta.model_name,
        object_id=str(obj.pk),
        object_repr=str(obj),
        object_data=data_snapshot,  # داده‌ها اینجا ثبت می‌شن
        extra_info=(extra_info or "") + f" | IP: {ip} | UA: {ua}",
    )
