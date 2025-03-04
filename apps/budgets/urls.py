from django.urls import path

from .views import GetCurrentBudgetView, UpdateBudgetView


urlpatterns = [
    path("", GetCurrentBudgetView.as_view(), name="get_current_budget"),
    path("update/",UpdateBudgetView.as_view(), name="update_budget"),
]
