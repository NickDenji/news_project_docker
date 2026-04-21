from django.shortcuts import render
from .models import Article, User, Newsletter
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .serializers import ArticleSerializer
from rest_framework import status
from .permissions import IsJournalist
from .permissions import IsEditorOrJournalist
from .permissions import IsEditor
from rest_framework.generics import CreateAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
import requests
from django.contrib.auth import login
from .permissions import IsReader
from django.core.mail import send_mail
from django.contrib import messages

# Create your views here.


@login_required
def update_article(request, article_id):
    """
    Allows a journalist (author) or editor to update an article.
    """

    article = get_object_or_404(Article, id=article_id)

    if request.user != article.author and request.user.role != "editor":
        return redirect("home")

    if request.method == "POST":
        article.title = request.POST.get("title")
        article.content = request.POST.get("content")
        article.save()
        messages.success(request, "Article updated successfully")
        return redirect("home")

    return render(request, "news_app/update_article.html", {"article": article})


def register(request):
    """
    Handles user registration with password confirmation.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')

        if password != confirm_password:
            return render(request, 'news_app/register.html', {
                'error': 'Passwords do not match'
            })

        user = User.objects.create_user(
            username=username,
            password=password,
            role=role
        )

        login(request, user)
        return redirect('home')

    return render(request, 'news_app/register.html')


def home(request):
    """
    Home page forces authentication before access.
    """

    if not request.user.is_authenticated:
        return redirect("/login/")

    if request.user.role == "reader":
        journalists = User.objects.filter(role="journalist")
        return render(request, "news_app/home.html", {
            "journalists": journalists,
            "is_reader": True
        })

    if request.user.role == "editor":
        articles = Article.objects.all()
        return render(request, "news_app/home.html", {
            "articles": articles,
            "is_reader": False
        })

    if request.user.role == "journalist":
        articles = Article.objects.filter(author=request.user)
        return render(request, "news_app/home.html", {
            "articles": articles,
            "is_reader": False
        })


@login_required
def subscribe(request, user_id):
    """
    Allows a reader to subscribe to a journalist.
    Prevents duplicate subscriptions.
    """
    if request.user.role != "reader":
        return redirect("home")

    journalist = User.objects.get(id=user_id)

    if journalist.role != "journalist":
        return redirect("home")

    # Only add if not already subscribed
    if journalist not in request.user.subscribed_journalists.all():
        request.user.subscribed_journalists.add(journalist)

    return redirect("home")


@login_required
def unsubscribe(request, user_id):
    """
    Allows a reader to unsubscribe from a journalist.
    """
    journalist = User.objects.get(id=user_id)
    request.user.subscribed_journalists.remove(journalist)
    return redirect("home")


def is_editor(user):
    """
    Check whether a given user has the 'editor' role.

    This function is typically used with decorators such as
    `user_passes_test` to restrict access to views that require
    editor-level permissions.

    Args:
        user (User): The user instance to be checked.

    Returns:
        bool: True if the user has the role 'editor', otherwise False.
    """
    return user.role == "editor"


def approve_article(request, article_id):
    """
    Allows only editors to approve articles and triggers API notification.
    """
    article = Article.objects.get(id=article_id)

    if request.user.role != "editor":
        return redirect("home")

    article.approved = True
    article.save()

    send_mail(
        subject="Article Approved",
        message=f"Your article '{article.title}' has been approved.",
        from_email="admin@example.com",
        recipient_list=[article.author.email or "test@example.com"],
        fail_silently=True,
    )

    return redirect("home")


@login_required
def create_article(request):
    """
    Allows journalists to create articles via UI.
    """
    if request.user.role != "journalist":
        return redirect("home")

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        Article.objects.create(
            title=title,
            content=content,
            author=request.user,
            approved=False,
        )

        return redirect("home")

    return render(request, "news_app/create_article.html")


@login_required
def delete_article(request, article_id):
    """
    Allows a journalist (author) or editor to delete an article.
    """

    article = get_object_or_404(Article, id=article_id)

    if request.user != article.author and request.user.role != "editor":
        return redirect("home")

    article.delete()
    messages.success(request, "Article deleted")
    return redirect("home")


@login_required
def subscribed_articles(request):
    """
    Displays articles from subscribed journalists (UI version).
    """

    if request.user.role != "reader":
        return redirect("home")

    articles = Article.objects.filter(
        approved=True,
        author__in=request.user.subscribed_journalists.all()
    )

    return render(request, "news_app/subscribed.html", {
        "articles": articles
    })


@login_required
def create_newsletter(request):
    """
    Allows ONLY journalists to create newsletters.
    """

    if request.user.role != "journalist":
        return redirect("home")

    articles = Article.objects.filter(author=request.user)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        selected_articles = request.POST.getlist("articles")

        newsletter = Newsletter.objects.create(
            title=title,
            description=description,
            author=request.user
        )

        newsletter.articles.set(selected_articles)

        return redirect("newsletters")

    return render(request, "news_app/create_newsletter.html", {
        "articles": articles
    })


@login_required
def article_detail(request, article_id):
    """
    Displays full article content.
    """
    article = get_object_or_404(Article, id=article_id)

    return render(request, "news_app/article_detail.html", {
        "article": article
    })


@login_required
def update_newsletter(request, newsletter_id):
    """
    Allows journalists (owner) or editors to edit a newsletter,
    but only with articles belonging to the newsletter author.
    """

    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    if request.user.id != newsletter.author.id and request.user.role != "editor":
        return redirect("home")

    articles = Article.objects.filter(author=newsletter.author)

    if request.method == "POST":
        newsletter.title = request.POST.get("title")
        newsletter.description = request.POST.get("description")

        selected_articles = request.POST.getlist("articles")

        newsletter.save()
        newsletter.articles.set(selected_articles)

        return redirect("newsletters")

    return render(request, "news_app/update_newsletter.html", {
        "newsletter": newsletter,
        "articles": articles
    })


@login_required
def delete_newsletter(request, newsletter_id):
    """
    Allows journalists or editors to delete a newsletter.
    """
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    if request.user != newsletter.author and request.user.role != "editor":
        return redirect("home")

    newsletter.delete()
    return redirect("newsletters")


@login_required
def list_newsletters(request):
    """
    Displays all newsletters.
    """

    newsletters = Newsletter.objects.all()

    return render(request, "news_app/newsletters.html", {
        "newsletters": newsletters
    })


@login_required
def subscribe_newsletter(request, newsletter_id):
    """
    Allows a reader to subscribe to a newsletter.
    """

    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    request.user.subscribed_publishers.add(newsletter)

    messages.success(request, "Subscribed to newsletter")
    return redirect("newsletters")


@login_required
def approve_article(request, article_id):
    """
    Allows editors to approve an article and triggers email notification.
    """

    article = get_object_or_404(Article, id=article_id)

    if request.user.role != "editor":
        return redirect("home")

    article.approved = True
    article.save()

    send_mail(
        subject="Article Approved",
        message=f"Your article '{article.title}' has been approved.",
        from_email="admin@example.com",
        recipient_list=[article.author.email or "test@example.com"],
        fail_silently=True,
    )

    messages.success(request, "Article approved")

    return redirect("home")


class ArticleListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns all approved articles.
        """
        articles = Article.objects.filter(approved=True)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


class SubscribedArticlesAPIView(APIView):
    permission_classes = [IsAuthenticated, IsReader]

    def get(self, request):
        """
        Returns articles from subscribed publishers and journalists.
        Accessible only to readers.
        """
        user = request.user

        articles = Article.objects.filter(approved=True).filter(
            Q(author__in=user.subscribed_journalists.all())
            | Q(publisher__in=user.subscribed_publishers.all())
        )

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


class ArticleDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Retrieve a single article by its primary key.

        This endpoint returns the details of a specific article.
        The user must be authenticated to access this view.

        Args:
            request (Request): The HTTP request object.
            pk (int): The primary key of the article to retrieve.

        Returns:
            Response: A JSON response containing the serialized article data.

        Raises:
            Article.DoesNotExist: If no article exists with the given primary key.
        """
        article = Article.objects.get(pk=pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)


class ArticleCreateAPIView(CreateAPIView):
    """
    Allows journalists to create articles.
    """

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsJournalist]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ArticleUpdateAPIView(UpdateAPIView):
    """
    Allows editors and journalists to update articles.
    """

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsEditorOrJournalist]

    def perform_update(self, serializer):
        article = self.get_object()

        # Journalists can only edit their own articles
        if (
            self.request.user.role == "journalist"
            and article.author != self.request.user
        ):
            raise PermissionDenied("You can only edit your own articles.")

        serializer.save()


class ArticleDeleteAPIView(DestroyAPIView):
    """
    Allows editors to delete articles.
    """

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsEditor]


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approved_article_log(request):
    """
    Logs approved articles (simulating external API).
    """

    article_id = request.data.get("article_id")

    return Response({"message": f"Article {article_id} received by external API"})
