from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    # Additional fields can be added here if needed
    pass

class Movie(models.Model):
    title = models.CharField(max_length=255, db_index=True)  # Added index
    description = models.TextField()
    actors = models.ManyToManyField(to='Actor', related_name="movies")
    genres = models.ManyToManyField(to='Genre', related_name="movies")

    def __str__(self):
        return self.title

class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"<Order: {self.created_at}>"

class Ticket(models.Model):
    movie_session = models.ForeignKey('MovieSession', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tickets')
    row = models.IntegerField()
    seat = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['row', 'seat', 'movie_session'], name='unique_seat')
        ]

    def clean(self):
        if self.row > self.movie_session.cinema_hall.rows or self.seat > self.movie_session.cinema_hall.seats_in_row:
            raise ValidationError(_('Seat or row is out of range'), code='invalid')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"<Ticket: {self.movie_session.movie.title} {self.movie_session.show_time} (row: {self.row}, seat: {self.seat})>"
