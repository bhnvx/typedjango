from backend.apps.core.urls import viewset_path
from .views import UserView

urlpatterns = [
    viewset_path(UserView, "users"),
]
