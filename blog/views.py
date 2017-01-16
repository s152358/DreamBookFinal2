from django.utils import timezone
from .models import Post, Comment, VoteUser
from django.shortcuts import render, get_object_or_404
from .forms import PostForm, CommentForm, RegistrationForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from rest_framework import generics
from .serializers import CommentSerializer


def author_check(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return post.author.endwith(request.user)

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})
@login_required

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            '''post.published_date = timezone.now()'''
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})
@login_required

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author==request.user :
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.published_date = timezone.now()
                post.save()
                return redirect('post_detail', pk=post.pk)
        else:
            form = PostForm(instance=post)
        return render(request, 'blog/post_edit.html', {'form': form})
@login_required

def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})
@login_required

def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author==request.user :
        post.delete()
        return redirect('post_list')

def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})



def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'],password=form.cleaned_data['password1'],email=form.cleaned_data['email'])
            return HttpResponseRedirect('/')
    form = RegistrationForm()
    variables = RequestContext(request, {'form': form})
    return render_to_response('registration/register.html',variables)

def view_profile(request, pk):
    posts = Post.objects.filter(author=pk, published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/profile.html', {'posts': posts})
@login_required
def dream_vote(request,pk):
    post = get_object_or_404(Post, pk=pk)
    if len(VoteUser.objects.filter(user=request.user, post=post)) < 1:
        post.vote_count_up()
        user_voted = VoteUser(user=request.user, post=post)
        user_voted.save()
        return redirect('post_detail', pk=post.pk)
    else:
        post.vote_count_up_undo()
        VoteUser.objects.filter(user=request.user, post=post).delete()
        return redirect('post_detail', pk=post.pk)

@login_required
def nightmare_vote(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if len(VoteUser.objects.filter(user=request.user, post=post)) < 1:
        post.vote_count_down()
        user_voted = VoteUser(user=request.user, post=post)
        user_voted.save()

        return redirect('post_detail', pk=post.pk)
    else:
        post.vote_count_down_undo()
        VoteUser.objects.filter(user=request.user, post=post).delete()
        return redirect('post_detail', pk=post.pk)

class PostsList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class PostsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
