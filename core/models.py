from django.db import models
from django.contrib.auth.models import User




class Game(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_date = models.DateField()
    cover = models.ImageField(upload_to='games/', blank=True)

    def __str__(self):
        return self.title




class GameRequirement(models.Model):
    game = models.OneToOneField(
        Game,
        on_delete=models.CASCADE,
        related_name='requirements'
    )

    minimum_cpu = models.CharField(max_length=200, blank=True)
    minimum_gpu = models.CharField(max_length=200, blank=True)
    minimum_ram_gb = models.IntegerField()

    recommended_cpu = models.CharField(max_length=200, blank=True)
    recommended_gpu = models.CharField(max_length=200, blank=True)
    recommended_ram_gb = models.IntegerField()

    minimum_storage = models.CharField(max_length=100, blank=True)
    recommended_storage = models.CharField(max_length=100, blank=True)

    minimum_network = models.CharField(max_length=200, blank=True)
    recommended_network = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.game.title} - Requirements"



class WishlistEntry(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist_entries'
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'game'],
                name='unique_wishlist_game'
            )
        ]

    def __str__(self):
        return f"{self.user.username} wants {self.game.title}."



class FriendRequest(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_friend_requests'
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_friend_requests'
    )

    status = models.CharField(
        max_length=10,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted')
        ],
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['sender', 'receiver'],
                name='unique_friend_request'
            )
        ]

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"



#VIDEO TUTORIAL
class VideoTutorial(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='tutorials'
    )

    publisher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='published_tutorials'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    video = models.FileField(
        upload_to='tutorials/'
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class TutorialPurchase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tutorial_purchases'
    )

    tutorial = models.ForeignKey(
        VideoTutorial,
        on_delete=models.CASCADE,
        related_name='purchases'
    )

    price_paid = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    purchased_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'tutorial'],
                name='unique_tutorial_purchase'
            )
        ]

    def __str__(self):
        return f"{self.user.username} bought {self.tutorial.title}"




class Review(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    comment = models.TextField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'game'],
                name='unique_user_review'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.game.title}"


#CHAT

class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )

    text = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"


#USER BLOCK

class UserBlock(models.Model):
    blocker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocked_users'
    )

    blocked = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocked_by_users'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['blocker', 'blocked'],
                name='unique_user_block'
            )
        ]

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"