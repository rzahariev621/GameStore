from django.db import models
from django.contrib.auth.models import User




class Game(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    release_date = models.DateField()
    cover = models.ImageField(upload_to='games/', blank=True)

    def __str__(self):
        return self.title




class LibraryEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='library_entries')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'game'],name='unique_library_game')]

    def __str__(self):
        return f"{self.user.username} owns {self.game.title}."




class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'game'],name='unique_user_purchase')]

    def __str__(self):
        return f"{self.user.username} bought {self.game.title}."




class Review(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'game'],
                name='unique_user_review'
            )
        ]

    def __str__(self):
        return f"{self.user.username} rated {self.game.title}."




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