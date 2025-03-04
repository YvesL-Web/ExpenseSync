from django.urls import path

from .views import (
    CreateTransactionAPIView,
    DeleteTransactionAPIView,
    GetAllTransactionsAPIView,
    AIReceiptScanner,
    GetTransaction,
    UpdateTransaction
)

urlpatterns = [
    path("", GetAllTransactionsAPIView.as_view(), name="get-all-transactions"),
    path("create-transaction/", CreateTransactionAPIView.as_view(), name="create-transaction"),
    path("delete-transactions/", DeleteTransactionAPIView.as_view(), name="delete-transactions"),
    path('scan-receipt/', AIReceiptScanner.as_view(), name='scan-receipt'),
    path("<str:transaction_id>/", GetTransaction.as_view(), name="get-transaction" ),
    path("update/<str:transaction_id>/", UpdateTransaction.as_view(), name="update-transaction" ),
]
