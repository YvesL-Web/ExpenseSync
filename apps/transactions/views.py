import base64
import logging
import json
import io

from datetime import timedelta
from decimal import Decimal
from uuid import UUID

from django.core.cache import cache
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction as db_transaction
# from rest_framework.throttling import UserRateThrottle
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from google.generativeai import GenerativeModel
from google.api_core.exceptions import GoogleAPIError

from PIL import Image

from apps.transactions.serializers import CreateTransactionSerializer, TransactionSerializer
from apps.accounts.models import Account
from config.utils.renderers import GenericJSONRenderer
from .models import Transaction


# Create your views here.

logger = logging.getLogger(__name__)


class GetAllTransactionsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        transactions = Transaction.objects.filter(user=user)
        return Response(
            TransactionSerializer(transactions, many=True).data,
            status=status.HTTP_200_OK,
        )


class CreateTransactionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [GenericJSONRenderer]
    object_label = "transaction"

    def get_account_object(self, account_id):
        try:
            UUID(str(account_id))
            return Account.objects.get(id=account_id)
        except (ValueError, ValidationError) as e:
            logger.error(str(e))
            return None
        except Account.DoesNotExist:
            return None

    def post(self, request, *args, **kwargs):
        serializer = CreateTransactionSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        data = serializer.validated_data

        account = self.get_account_object(data["account_id"])
        if account is None:
            return Response({"detail": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        if account.user != self.request.user:
            raise PermissionDenied("You do not have permissions.")

        if data["isRecurring"] and ("recurringInterval" not in data or data["recurringInterval"] == ""):
            return Response({
                "detail": "if is recurring is set to true then you have to provide a recurring interval (daily,weekly monthly,yearly) !"
            }, status=status.HTTP_400_BAD_REQUEST)

        # calculer le nouveau solde du compte
        balance_change = 0
        if data["type"] == "expense":
            balance_change -= data["amount"]
        else:
            balance_change += data["amount"]
        new_balance = account.balance + balance_change

        try:
            with db_transaction.atomic():
                # Créer la transaction
                Transaction.objects.create(
                    user=request.user,
                    account=account,
                    type=data["type"],
                    amount=data["amount"],
                    description=data["description"],
                    receiptUrl=data["receiptUrl"],
                    date=data["date"],
                    category=data["category"],
                    isRecurring=data["isRecurring"],
                    recurringInterval=data["recurringInterval"],
                    nextRecurringDate=self.calculate_next_recurring_date(
                        data) if data.get("isRecurring") else None,
                    status="completed"
                )

                # Mettre à jour le solde du compte
                account.balance = new_balance
                account.save()

            return Response(
                {
                    "success": True,
                    "detail": "Transaction successfully created.",
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(str(e))
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def calculate_next_recurring_date(self, data):
        """
        Calcule la prochaine date de récurrence en fonction de l'intervalle.
        """
        if not data.get('isRecurring') or not data.get('recurringInterval'):
            return None

        interval = data['recurringInterval']
        date = data['date']

        if (interval).lower() == 'daily':
            return date + timedelta(days=1)
        elif (interval).lower() == 'weekly':
            return date + timedelta(weeks=1)
        elif (interval).lower() == 'monthly':
            return date + timedelta(days=30)  # Approximation
        elif (interval).lower() == 'yearly':
            return date + timedelta(days=365)  # Approximation
        else:
            return None


class GetTransaction(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, user, transaction_id):
        """
        Récupère une transaction par son utilisateur et son ID ou retourne None si elle n'existe pas.
        """
        
        try:
            transaction = Transaction.objects.get(user=user, id=transaction_id)
            return transaction
        except ValidationError as e:
            logger.error(str(e))
            return None
        except Transaction.DoesNotExist:
            return None

    def get(self, request, transaction_id):
        transaction = self.get_object(request.user, transaction_id)
        if transaction is None:
            return Response(
                {"detail": "Transaction not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            TransactionSerializer(transaction).data,
            status=status.HTTP_200_OK,
        )


class UpdateTransaction(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, user, transaction_id):
        """
        Récupère une transaction par son utilisateur et son ID ou retourne None si elle n'existe pas.
        """
       
        try:
            transaction = Transaction.objects.get(user=user, id=transaction_id)
            return transaction
        except (ValueError, ValidationError) as e:
            logger.error(str(e))
            return None
        except Transaction.DoesNotExist:
            return None

    def put(self, request, transaction_id):
        transaction = self.get_object(request.user, transaction_id)
        if transaction is None:
            return Response(
                {"detail": "Transaction not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TransactionSerializer(
            transaction, data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            # Calculer les changements
            old_balance = 0
            new_balance = 0

            if transaction.type == "expense":
                old_balance -= transaction.amount
            else:
                old_balance += transaction.amount

            if data["type"] == "expense":
                new_balance -= data["amount"]
            else:
                new_balance += data["amount"]

            net_balance_change = new_balance - old_balance

            try:
                with db_transaction.atomic():
                    updated_transaction = serializer.save()
                    # Mettre à jour le solde du compte
                    account = updated_transaction.account
                    account.balance += net_balance_change
                    account.save()
                return Response({
                    "detail": "Transaction successfully updated."
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(
                    f"Error while trying to update the transaction: {str(e)}")
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class DeleteTransactionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [GenericJSONRenderer]

    def delete(self, request):
        transaction_ids = request.data.get("transaction_ids", [])

        if not transaction_ids:
            return Response(
                {
                    "success": False,
                    "error": "No transaction ID provided."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with db_transaction.atomic():
                transaction_to_delete = Transaction.objects.filter(
                    id__in=transaction_ids)
                if not transaction_to_delete.exists():
                    return Response(
                        {
                            "success": False,
                            "error": "No transactions found with the IDs provided."
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

                account = transaction_to_delete.first().account

                total_amount_to_remove = Decimal('0.0')
                for trans in transaction_to_delete:
                    if trans.type == "income":
                        total_amount_to_remove -= trans.amount
                    else:
                        total_amount_to_remove += trans.amount

                transaction_to_delete.delete()

                account.balance += total_amount_to_remove
                account.save()

                return Response(
                    {
                        "success": True,
                        "message": f"{len(transaction_ids)} successfully deleted transactions.",
                        # Convertir en float pour la sérialisation JSON
                        "new_balance": float(account.balance),
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            logger.error(str(e))
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AIReceiptScanner(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # renderer_classes = [GenericJSONRenderer]

    def post(self, request, *args, **kwargs):
        # Verifier si un fichier a été envoyé
        print(f"REQUEST: {request.FILES}")
        if "file" not in request.FILES:
            return Response({
                "detail": "No files were provided!"
            }, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES["file"]

        # Validation du type de fichier   # "application/pdf"
        allowed_types = ["image/jpeg", "image/png", "image/jpg"]
        if file.content_type not in allowed_types:
            return Response(
                {"detail": "The file must be an image from type (JPEG, PNG, JPG, PDF)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validation de la taille du fichier (5Mo maximum)
        max_size = 5 * 1024 * 1024  # 5 Mo
        if file.size > max_size:
            return Response(
                {"detail": "The file must not exceed 5Mo."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(file, InMemoryUploadedFile):
            return Response({
                "detail": "The file provided is invalid."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Générer une clé de cache unique pour le fichier
        file_hash = self.calculate_file_hash(file)
        cached_result = cache.get(file_hash)

        if cached_result:
            return Response(cached_result, status=status.HTTP_200_OK)

        try:
            # convertir l'image en base64
            image = Image.open(file)
            buffered = io.BytesIO()
            image.save(buffered, format=image.format)
            base64_string = base64.b64encode(
                buffered.getvalue()).decode("utf-8")

            # Initialiser le mod`le Gemini
            model = GenerativeModel("gemini-1.5-flash")

            # Définir le prompt
            prompt = """
                Analyze this receipt image and extract the following information in JSON format:
                - Total amount (just the number)
                - Date (in ISO format)
                - Description or items purchased (brief summary)
                - Merchant/store name
                - Suggested category (one of: housing,transportation,groceries,utilities,entertainment,food,shopping,healthcare,education,personal,travel,insurance,gifts,bills,other-expense)

                Only respond with valid JSON in this exact format:
                {
                    "amount": number,
                    "date": "ISO date string",
                    "description": "string",
                    "merchantName": "string",
                    "category": "string"
                }

                If it's not a receipt, return an empty object.
            """

            # Envoyer l'image et le prompt à Gemini
            result = model.generate_content([
                {
                    "inline_data": {
                        "data": base64_string,
                        "mime_type": file.content_type
                    },
                },
                prompt,
            ])

            # Récupérer et nettoyer la réponse
            response_text = result.text.replace(
                "```json", "").replace("```", "").strip()

            # Convertir la réponse ne JSON
            try:
                data = json.loads(response_text)
                if not data:  # Si l'object est vide
                    return Response(
                        {"detail": "The file provided is not a valid invoice."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Formater les données de réponse
                response_data = {
                    "amount": float(data.get("amount", 0)),
                    "date": data.get("date"),
                    "description": data.get("description"),
                    "merchantName": data.get("merchantName"),
                    "category": data.get("category"),
                }

                # Mettre en cache le résultat
                # Cache pour 1 heure
                cache.set(file_hash, response_data, timeout=60 * 60)

                return Response(response_data, status=status.HTTP_200_OK)

            except json.JSONDecodeError:
                logger.error("Gemini's response is not in valid JSON format.")
                return Response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except GoogleAPIError as e:
            logger.error(f"Error when calling Gemini: {str(e)}")
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def calculate_file_hash(self, file):
        """
        Calcule un hash unique pour le fichier.
        """
        file.seek(0)
        file_content = file.read()
        import hashlib
        return hashlib.md5(file_content).hexdigest()
