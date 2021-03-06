import json 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import  HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post


def index(request):
    posts = Post.objects.all().order_by('timestamp').reverse()
    page = request.GET.get("page", 1)
    paginator = Paginator(posts, 10)

    try:
        posts = paginator.page(page)

    except PageNotAnInteger:
        posts = paginator.page(1)

    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, "network/index.html", {
        "posts":posts
        })

def user(request, user_id):
    try:
        logged_in_user = request.user
        current_user = User.objects.get(pk=user_id)
    except User.DoesNotExist as error:
        messages.add_messgage(request, messages.ERROR, error, extra_tags="bid")
        return HttpResponseRedirect(reverse("network:index"))
    
    is_followed = (
        current_user.following.all().filter(pk=logged_in_user.pk).exists()
    )

    if request.method == "POST":
        if "follow" in request.POST:
            is_followed = toggle_followed(logged_in_user, current_user)
            return HttpResponseRedirect(
                reverse("network:user", kwargs={"user_id": user_id})
            )
    
    fetched_following = (
        User.objects.all().filter(following=current_user).count()
    )
    fetched_followers = (
        User.objects.all().filter(followers=current_user).count()
    )
    fetched_posts = (
        Post.objects.filter(user=current_user).order_by("timestamp").reverse()
    )
    page = request.GET.get("page", 1)
    paginator = Paginator(fetched_posts, 10)

    try:
        fetched_posts = paginator.page(page)
    except PageNotAnInteger:
        fetched_posts = paginator.page(1)
    except EmptyPage:
        fetched_posts = paginator.page(paginator.num_pages)

    return render(
        request,
        "network/user.html",
        {
            "is_followed": is_followed,
            "logged_in_user": logged_in_user,
            "current_user": current_user,
            "posts": fetched_posts,
            "following": fetched_following,
            "followers": fetched_followers,
        },
    )


def following(request):
    posts=[]

    page = request.GET.get("page", 1)
    paginator = Paginator(posts, 10)

    fetched_user = User.objects.get(email=request.user.email)
    fetched_following = User.objects.all().filter(following=fetched_user)

    for f in fetched_following:
        fetched_posts = list(Post.objects.filter(user=f))
        for fpost in fetched_posts:
            posts.append(fpost)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    return render(request, "network/following.html", {
        "posts":posts
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        #return reverse("network:register")
        #return HttpResponseRedirect(reverse("network:register"))
        return render(request, "network/register.html")


def newpost(request):
    if request.method == "POST" and request.user.is_authenticated:
        fetched_user = User.objects.get(email=request.user.email)

        if "post" in request.POST:
            body = request.POST["post-body"]
            p = Post.objects.create(user=fetched_user, body=body)
            p.save()
            return HttpResponseRedirect(reverse("network:index"))


def post(request, post_id):

    try:
        post = Post.objects.get(pk=post_id)
        
    except Post.DoesNotExist:
        return JsonResponse({"error"}, status=404)

    if request.method == "PUT" and request.user.is_authenticated:
        data = json.loads(request.body)

        if data.get("userId") is not None and data.get("postId") is not None:
            user_id = data.get("userId")
            toggle_liked(user_id, post_id)
            return HttpResponse(status=204)

        if data.get("body") is not None:
            post.body = data["body"]
            post.save()
            return HttpResponse(status=204)
    return JsonResponse({"error": "401 Unauthorized"}, status=401)



def toggle_followed(logged_in_user, current_user):

    # is logged in user following current user
    LF = (current_user.following.all().filter(pk=logged_in_user.pk).exists())

    if LF:
        logged_in_user.followers.remove(current_user)
    else:
        logged_in_user.followers.add(current_user)
    
    return LF

def toggle_liked(logged_in_user_id, post_id):

    fetchedPost = Post.objects.get(pk=post_id)
    fetchedUser = User.objects.get(pk=logged_in_user_id)

    userLikesCurrentPost = (fetchedPost.likes.all().filter(pk=logged_in_user_id).exists())

    if userLikesCurrentPost:
        fetchedPost.likes.remove(fetchedUser)
    else:
        fetchedPost.likes.add(fetchedUser)
    fetchedPost.save()

    return userLikesCurrentPost

