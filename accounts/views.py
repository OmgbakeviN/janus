from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def signup(request):
    """
    Permet à un utilisateur de créer un compte.
    - GET : affiche le formulaire
    - POST : valide et crée l'utilisateur
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Crée l'utilisateur
            return redirect("login")  # Redirige vers la page de login
    else:
        form = UserCreationForm()

    return render(request, "accounts/signup.html", {"form": form})

