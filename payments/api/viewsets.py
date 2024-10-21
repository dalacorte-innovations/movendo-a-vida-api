from datetime import timezone
import stripe
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from users.models import User
from payments.models import Product
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        token = request.data.get('stripeToken')
        stripe_product_id = request.data.get('product_id')
        amount = request.data.get('amount')

        try:
            product = Product.objects.get(stripe_product_id=stripe_product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Produto não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if not user.stripe_customer_id:
            try:
                customer = stripe.Customer.create(
                    email=user.email,
                    source=token
                )
                user.stripe_customer_id = customer.id
                user.save()
            except stripe.error.StripeError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            charge = stripe.Charge.create(
                customer=user.stripe_customer_id,
                amount=amount,
                currency="brl",
                description=f"Pagamento para o produto: {product.name}"
            )

            user.payment_made = True
            user.last_payment = timezone.now()
            user.plan = product
            user.save()

            return Response({
                "message": "Pagamento realizado com sucesso",
                "charge": charge,
                "product": product.name
            }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
