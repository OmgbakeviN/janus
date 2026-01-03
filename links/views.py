from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from .models import ShortLink, ClickEvent
from .forms import ShortLinkForm

import uuid
# Create your views here.

def landing(request):
    """
    Page d’accueil publique.
    L’utilisateur arrive ici avant de créer un compte ou de se connecter.
    """
    return render(request, "landing.html")

@login_required
def dashboard(request):
    """
    Page du dashboard.
    L’utilisateur arrive ici après s'être connecté.
    on affiche les liens du user connecté
    """
    links = ShortLink.objects.filter(owner=request.user).order_by("-created_at")
    return render(request, "links/dashboard.html", {"links": links})

@login_required
def link_create(request):
    """
    Permet de créer un nouveau lien :
    - GET : affiche le formulaire
    - POST : crée le lien puis redirige vers le dashboard (pour l’instant)
    """
    if request.method == "POST":
        form = ShortLinkForm(request.POST)
        if form.is_valid():
            form.save(owner=request.user)
            return redirect("links:dashboard")
    else:
        form = ShortLinkForm()

    return render(request, "links/link_form.html", {"form": form})

def get_client_ip(request):
    """
    Récupère l'IP du client.
    Si l'app est derrière un proxy (Render, Nginx...), X-Forwarded-For peut exister.
    """
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

def get_or_set_visitor_id(request):
    """
    Récupère un identifiant visiteur depuis un cookie.
    Si absent, on en crée un nouveau (uuid).
    """
    visitor_id = request.COOKIES.get("visitor_id", "")
    if not visitor_id:
        visitor_id = uuid.uuid4().hex
    return visitor_id

@login_required
def link_detail(request, pk):
    """
    Page détail d'un lien (dashboard du lien).
    - Affiche l'URL originale
    - Affiche l'URL courte
    - Affiche des stats simples : total clicks + unique clicks + top referrers
    """
    link = get_object_or_404(ShortLink, pk=pk, owner=request.user)

    # URL courte complète (ex: http://127.0.0.1:8000/r/abc123/)
    short_url = request.build_absolute_uri(reverse("links:redirect", args=[link.slug]))

    total_clicks = link.clicks.count()

    # Clics uniques basés sur visitor_id (cookie)
    unique_clicks = link.clicks.exclude(visitor_id="").values("visitor_id").distinct().count()

    # Top referrers (d'où viennent les clics)
    top_referrers = (
        link.clicks.exclude(referrer="")
        .values("referrer")
        .annotate(c=Count("id"))
        .order_by("-c")[:5]
    )

    context = {
        "link": link,
        "short_url": short_url,
        "total_clicks": total_clicks,
        "unique_clicks": unique_clicks,
        "top_referrers": top_referrers,
    }
    return render(request, "links/link_detail.html", context)

def redirect_short(request, slug):
    """
    Endpoint public :
    - Enregistre le clic
    - Redirige immédiatement vers l'URL originale
    """
    link = get_object_or_404(ShortLink, slug=slug, is_active=True)

    visitor_id = get_or_set_visitor_id(request)

    # Headers utiles pour analytics
    ip = get_client_ip(request)
    ua = request.META.get("HTTP_USER_AGENT", "")
    ref = request.META.get("HTTP_REFERER", "")
    lang = request.META.get("HTTP_ACCEPT_LANGUAGE", "")

    # On enregistre un ClickEvent
    ClickEvent.objects.create(
        link=link,
        visitor_id=visitor_id,
        ip_address=ip,
        user_agent=ua,
        referrer=ref,
        accept_language=lang,
    )

    # Redirection vers l'URL originale (302)
    response = redirect(link.original_url)

    # On place le cookie 1 an, pour mesurer "unique clicks"
    response.set_cookie(
        "visitor_id",
        visitor_id,
        max_age=60 * 60 * 24 * 365,
        samesite="Lax",
    )
    return response



