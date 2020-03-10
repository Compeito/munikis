def notification(request):
    not_reads_count = 0
    if request.user.is_authenticated:
        # target=Noneはメール連投対策のために削除せず、除外することで対応する
        not_reads = request.user.received_notifications.filter(is_read=False)
        not_reads_count = len([n for n in not_reads if n.target])
    return {'not_reads_count': not_reads_count}
