from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class ThreadManager(models.Manager):
    def by_user(self, user):
        return self.get_queryset().filter(Q(first_person=user) | Q(second_person=user)).distinct()


class Thread(models.Model):
    first_person = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='thread_first_person', null=False
    )
    second_person = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='thread_second_person', null=False
    )
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    class Meta:
        unique_together = ['first_person', 'second_person']

    def save(self, *args, **kwargs):
        """Ensure consistent ordering of first_person and second_person."""
        if self.first_person and self.second_person and self.first_person.id > self.second_person.id:
            self.first_person, self.second_person = self.second_person, self.first_person
        super().save(*args, **kwargs)

    def get_last_message(self):
        """Retrieve the last message in the thread."""
        return self.chat_messages.order_by('-timestamp').first()

    def __str__(self):
        return f"Thread between {self.first_person} and {self.second_person}"


class ChatMessage(models.Model):
    thread = models.ForeignKey(
        Thread, null=True, blank=True, on_delete=models.CASCADE, related_name='chat_messages'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='chat_media/files/', blank=True, null=True)
    image = models.ImageField(upload_to='chat_media/images/', blank=True, null=True)
    audio = models.FileField(upload_to='chat_media/audio/', blank=True, null=True)
    voice_message = models.FileField(upload_to='chat_media/voice/', blank=True, null=True)  # Voice messages support
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        preview = self.message[:30] + "..." if self.message else "Media Message"
        return f"{self.user} ({self.timestamp}): {preview}"


class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='message_media/files/', blank=True, null=True)
    image = models.ImageField(upload_to='message_media/images/', blank=True, null=True)
    audio = models.FileField(upload_to='message_media/audio/', blank=True, null=True)
    voice_message = models.FileField(upload_to='message_media/voice/', blank=True, null=True)  # Added voice message support
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        preview = self.content[:30] + "..." if self.content else "Media Message"
        return f"From {self.sender} to {self.receiver} at {self.timestamp}: {preview}"
