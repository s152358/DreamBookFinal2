from django.db import models
from django.utils import timezone
from django.conf import settings

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, default = 1)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

    def approved_comments(self):
        return self.comments.filter(approved_comment=True)

    def vote_count_dream(self):
        return self.upvotes

    def vote_count_nightmare(self):
        return self.downvotes

    def vote_count_up(self):
        self.upvotes = self.upvotes + 1
        self.save()

    def vote_count_down(self):
        self.downvotes = self.downvotes + 1
        self.save()

    def vote_count_up_undo(self):
        self.upvotes = self.upvotes - 1
        self.save()

    def vote_count_down_undo(self):
        self.downvotes = self.downvotes - 1
        self.save()


class Comment(models.Model):
    post = models.ForeignKey('blog.Post', related_name='comments')
    author = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.text


class VoteUser(models.Model):
    post = models.ForeignKey('blog.Post', related_name='votes_post')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default = 1)

    def user_voted(self):
        self.has_voted = True
        self.save()
