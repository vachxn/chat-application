from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from chat.models import Thread

@login_required
def messages_page(request):
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread')
    context = {
        'threads': threads
    }
    return render(request, 'messages.html', context)
