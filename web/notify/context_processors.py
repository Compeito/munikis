def notification(request):
    not_reads_count = 0
    if request.user.is_authenticated:
        not_reads_count = request.user.received_notifications.filter(is_read=False).count()
    return {'not_reads_count': not_reads_count}
