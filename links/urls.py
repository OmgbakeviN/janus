from django.urls import path
from .views import dashboard, link_create, link_detail, redirect_short

app_name = "links"

urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("links/new/", link_create, name="create"),
    path("links/<int:pk>/", link_detail, name="detail"),
    path("r/<slug:slug>/", redirect_short, name="redirect"),
]

