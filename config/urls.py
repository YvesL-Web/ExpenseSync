from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/auth/", include("djoser.urls")),
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/profile/", include("apps.profiles.urls")),
    path("api/v1/account/", include("apps.accounts.urls")),
    path("api/v1/transactions/", include("apps.transactions.urls")),
    path("api/v1/budget/",include("apps.budgets.urls")),
]
