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
        
        try:
            user = User.objects.get(stripe_customer_id=stripe_customer_id)
            user.last_payment = timezone.now()
            user.payment_made = True
            user.save()
        except User.DoesNotExist:
            return JsonResponse({'status': 'user not found'}, status=404)

    return JsonResponse({'status': 'success'}, status=200)
