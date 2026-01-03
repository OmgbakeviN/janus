from django import forms
from .models import ShortLink

class ShortLinkForm(forms.ModelForm):
    """
    Formulaire de création d'un lien.
    On ajoute un champ custom_slug pour laisser l'utilisateur choisir un slug.
    """
    custom_slug = forms.CharField(
        max_length=32,
        required=False,
        help_text="Optionnel. Si vide, un slug sera généré automatiquement."
    )

    class Meta:
        model = ShortLink
        fields = ["title", "original_url"]

    def clean_custom_slug(self):
        """
        Vérifie que le slug custom n'est pas déjà pris.
        """
        val = (self.cleaned_data.get("custom_slug") or "").strip()
        if val and ShortLink.objects.filter(slug=val).exists():
            raise forms.ValidationError("Ce slug est déjà utilisé. Choisis-en un autre.")
        return val

    def save(self, owner, commit=True):
        """
        Sauvegarde en attachant le owner (user connecté).
        """
        obj = super().save(commit=False)
        obj.owner = owner

        custom = self.cleaned_data.get("custom_slug")
        if custom:
            obj.slug = custom  # Si l’utilisateur a donné un slug, on l’utilise.

        if commit:
            obj.save()
        return obj
