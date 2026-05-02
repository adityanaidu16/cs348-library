from django.db import models


class Member(models.Model):
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    email = models.EmailField(unique=True)
    membership_date = models.DateField()

    class Meta:
        indexes = [
            models.Index(fields=['age'], name='member_age_idx'),
        ]

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    total_copies = models.IntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(fields=['title'], name='book_title_idx'),
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"


class Loan(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    checkout_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['due_date'], name='loan_due_idx'),
            models.Index(fields=['return_date'], name='loan_return_idx'),
            models.Index(fields=['checkout_date'], name='loan_checkout_idx'),
        ]

    def __str__(self):
        return f"{self.member.name} - {self.book.title}"

    @property
    def is_overdue(self):
        from datetime import date
        if self.return_date:
            return False
        return date.today() > self.due_date
