from django.urls import path

from .views import (
    AccountCreateApiView,
    MyAccountsListApiView,
    UpdateDefaultAccount,
    GetAccountWithTransaction,
)

from .utils.poupulate_account_with_dumies_transactions import SeedTransactionsView

urlpatterns = [
    path("create/", AccountCreateApiView.as_view()),
    path("my-accounts/", MyAccountsListApiView.as_view()),
    path("<str:id>/", GetAccountWithTransaction.as_view()),
    path("<str:account_id>/update/", UpdateDefaultAccount.as_view()),
    # path('seed-transactions/', SeedTransactionsView.as_view()), 
]
