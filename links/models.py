import random
import string
import uuid

from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.
def generate_slug(length=6):
    """
    Génère un slug aléatoire (ex: aZ83kP).
    On l'utilise quand l'utilisateur ne fournit pas de slug personnalisé.
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))

class ShortLink(models.Model):
    """
    Représente un lien raccourci appartenant à un utilisateur.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="short_links",
    )

    title = models.CharField(max_length=120, blank=True)
    original_url = models.URLField(max_length=800)

    # blank=True pour permettre la création sans slug (on le génère dans save())
    slug = models.SlugField(max_length=32, unique=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.slug} -> {self.original_url}"

    def save(self, *args, **kwargs):
        """
        Si aucun slug n'est fourni, on en génère un automatiquement.
        On s'assure qu'il est unique.
        """
        if not self.slug:
            slug = generate_slug()
            while ShortLink.objects.filter(slug=slug).exists():
                slug = generate_slug()
            self.slug = slug

        super().save(*args, **kwargs)

class ClickEvent(models.Model):
    """
    Un événement de clic sur un lien raccourci.
    Chaque fois que quelqu'un clique sur /r/<slug>/, on crée une ligne ici.
    """
    link = models.ForeignKey(
        "ShortLink",
        on_delete=models.CASCADE,
        related_name="clicks"
    )

    clicked_at = models.DateTimeField(default=timezone.now)

    # Pour compter des "clics uniques" de façon simple (cookie)
    visitor_id = models.CharField(max_length=64, blank=True)

    # Infos récupérables côté serveur
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.TextField(blank=True)
    accept_language = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Click on {self.link.slug} at {self.clicked_at}"
