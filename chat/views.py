from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .forms import SignupForm, MessageForm
from .models import Message
from django.core.files.storage import default_storage

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'home')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    request.session.flush()
    logout(request)
    return redirect('login')

@login_required
def messages_page(request):
    users = User.objects.exclude(id=request.user.id)

    user_data = []
    for user in users:
        unread_count = Message.objects.filter(sender=user, receiver=request.user, read=False).count()
        user_data.append({"user": user, "unread_count": unread_count})

    return render(request, "messages.html", {"users": user_data})

@login_required
def chat(request, user_id):
    """
    Returns messages for the selected user.
    """
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        sender=request.user, receiver=other_user
    ) | Message.objects.filter(
        sender=other_user, receiver=request.user
    ).order_by("timestamp")

    messages_data = []
    for msg in messages:
        msg_data = {
            "text": msg.content,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "is_sender": msg.sender == request.user,
        }
        if msg.image:
            msg_data["image_url"] = msg.image.url
        if msg.file:
            msg_data["file_url"] = msg.file.url
        if msg.voice_message:
            msg_data["voice_url"] = msg.voice_message.url

        messages_data.append(msg_data)

    return JsonResponse({"messages": messages_data})

@login_required
def send_message(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('message', '')
        image = request.FILES.get('image')
        file = request.FILES.get('file')
        voice_message = request.FILES.get('voice')

        if receiver_id:
            receiver = get_object_or_404(User, id=receiver_id)

            message = Message.objects.create(
                sender=request.user, receiver=receiver, content=content
            )

            if image:
                message.image = image
            if file:
                message.file = file
            if voice_message:
                message.voice_message = voice_message

            message.save()

        return redirect('chat', user_id=receiver_id)
