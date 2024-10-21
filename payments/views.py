import json
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from users.models import User

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        return JsonResponse({'status': 'invalid payload'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        stripe_customer_id = session.get('customer')
        product_name = session.get('metadata', {}).get('product_name')

        try:
            user = User.objects.get(stripe_customer_id=stripe_customer_id)
        except User.DoesNotExist:
            user_email = session.get('customer_details').get('email')
            try:
                user = User.objects.get(email=user_email)
                user.stripe_customer_id = stripe_customer_id
            except User.DoesNotExist:
                return JsonResponse({'status': 'user not found'}, status=404)

        user.last_payment = timezone.now()
        user.payment_made = True
        user.plan = product_name
        user.next_payment = timezone.now() + timezone.timedelta(days=30)
        user.save()

    return JsonResponse({'status': 'success'}, status=200)
