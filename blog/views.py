from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Count, Q
from .models import Post, Category
from .forms import PostForm
from .forms import CommentForm
from taggit.models import Tag
from django.contrib.auth.models import User  # Import model User

from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages


@login_required
def profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        # Update nama pengguna jika ada perubahan
        if username and request.user.username != username:
            request.user.username = username
            request.user.save()
            messages.success(request, 'Nama pengguna berhasil diubah.')

        return redirect('blog:profile')

    return render(request, 'blog/profile.html')
def post_create(request):
    """Membuat postingan baru."""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save()
            return redirect(new_post.get_absolute_url())  # Redirect ke detail postingan
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

def post_edit(request, slug):
    """Mengedit postingan yang sudah ada."""
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect(post.get_absolute_url())  # Redirect ke detail postingan
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form})

def tag_list(request):
    tags = Tag.objects.all()  # Ambil semua tag
    return render(request, 'blog/tag_list.html', {'tags': tags})

def post_list(request):
    query = request.GET.get('q')  # Keyword pencarian
    category_slug = request.GET.get('category')  # Filter kategori
    tag_slug = request.GET.get('tag')  # Filter tag
    author_username = request.GET.get('author')  # Filter penulis
    sort_by_comments = request.GET.get('sort') == 'comments'  # Urutkan berdasarkan komentar
    order = request.GET.get('order')  # Urutkan berdasarkan tanggal

    # Ambil semua postingan dan anotasi dengan jumlah komentar aktif
    posts = Post.published.annotate(comment_count=Count('comments', filter=Q(comments__active=True)))

    # Filter berdasarkan pencarian
    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(body__icontains=query))

    # Filter berdasarkan kategori
    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    # Filter berdasarkan tag
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)

    # Filter berdasarkan penulis
    if author_username:
        posts = posts.filter(author__username=author_username)

    # Urutkan berdasarkan jumlah komentar jika opsi dipilih
    if sort_by_comments:
        posts = posts.order_by('-comment_count')

    # Urutkan berdasarkan tanggal jika dipilih
    if order == 'newest':
        posts = posts.order_by('-publish')  # Urutkan dari yang terbaru
    elif order == 'oldest':
        posts = posts.order_by('publish')  # Urutkan dari yang terlama

    # Pagination: 5 postingan per halaman
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Data untuk dropdown kategori, tag, dan penulis
    categories = Category.objects.all()
    tags = Tag.objects.all()
    authors = User.objects.filter(blog_posts__in=posts).distinct()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'authors': authors,
        'query': query,
        'sort_by_comments': sort_by_comments,
        'category_slug': category_slug,
        'tag_slug': tag_slug,
        'author_username': author_username,
        'order': order,
    }
    return render(request, 'blog/post_list.html', context)


def post_list_by_tag(request, tag_slug):
    """Menampilkan daftar postingan berdasarkan tag."""
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.published.filter(tags__in=[tag]).distinct()  # Pastikan tidak ada duplikasi

    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tag': tag,
        'page_obj': page_obj,
    }
    return render(request, 'blog/post_list.html', context)

def post_detail(request, year, month, day, slug):
    """Menampilkan detail postingan dan komentar terkait."""
    post = get_object_or_404(
        Post, slug=slug, status=Post.Status.PUBLISHED,
        publish__year=year, publish__month=month, publish__day=day
    )

    # Ambil hanya komentar aktif
    comments = post.comments.filter(active=True)

    # Pagination: 3 komentar per halaman
    paginator = Paginator(comments, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return redirect(post.get_absolute_url())  # Redirect ke halaman detail

    else:
        comment_form = CommentForm()

    context = {
        'post': post,
        'page_obj': page_obj,
        'comment_form': comment_form,
    }
    return render(request, 'blog/post_detail.html', context)


def post_list_by_category(request, slug):
    """Menampilkan daftar postingan berdasarkan kategori."""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.published.filter(category=category).distinct()

    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/post_list.html', context)


def post_list_by_tag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.published.filter(tags__in=[tag])

    paginator = Paginator(posts, 5)  # Pagination
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tag': tag,
        'page_obj': page_obj,
    }
    return render(request, 'blog/post_list.html', context)

def post_list_by_author(request, author_username):
    """Menampilkan daftar postingan berdasarkan penulis."""
    posts = Post.published.filter(author__username=author_username).distinct()

    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'author_username': author_username,
        'page_obj': page_obj,
    }
    return render(request, 'blog/post_list.html', context)


def post_list_by_date(request, year, month, day):
    """Menampilkan daftar postingan berdasarkan tanggal tertentu."""
    posts = Post.published.filter(
        publish__year=year, publish__month=month, publish__day=day
    ).distinct()

    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'year': year,
        'month': month,
        'day': day,
    }
    return render(request, 'blog/post_list.html', context)


def register(request):
    """Pendaftaran akun baru."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Login otomatis setelah berhasil register
            return redirect('blog:post_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'  # Pastikan path template benar
