import os
import stripe
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from plans_subscriptions.models import Plan, Subscription
from datetime import datetime, timedelta
from django.utils import timezone

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
User = get_user_model()

@csrf_exempt
def stripe_webhook(request):
    user_email = None
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({"error": "Webhook signature verification failed."}, status=400)

    event_type = event["type"]

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        user_email = session.get("customer_email")
        plan_id = session.get("metadata", {}).get("plan_id")

        if not user_email or not plan_id:
            return JsonResponse({"error": "user_email ou plan_id não encontrados"}, status=400)

        try:
            user = User.objects.get(email=user_email)
            plan = Plan.objects.get(id=plan_id)
            
            subscription, created = Subscription.objects.get_or_create(
                user=user,
                defaults={'start_date': timezone.now()}
            )

            date_script = subscription.start_date if subscription.start_date else timezone.now()
            subscription.plan = plan
            subscription.start_date = date_script
            subscription.stripe_subscription_id = session.get("subscription")
            subscription.active = False  
            subscription.save()

            print(f"✅ Assinatura criada para {user_email} no plano {plan.name}, aguardando ativação...")
            return JsonResponse({"message": "Assinatura criada e aguardando ativação"}, status=200)

        except User.DoesNotExist:
            print(f"❌ Erro: Usuário {user_email} não encontrado.")
            return JsonResponse({"error": "Usuário não encontrado"}, status=404)

        except Plan.DoesNotExist:
            print(f"❌ Erro: Plano {plan_id} não encontrado.")
            return JsonResponse({"error": "Plano não encontrado"}, status=404)

    elif event_type in ["customer.subscription.created", "customer.subscription.updated"]:
        subscription_data = event["data"]["object"]
        
        stripe_subscription_id = subscription_data.get("id")
        if user_email is None:
            user_email = subscription_data.get("metadata", {}).get("user_email")

        if not user_email:
            return JsonResponse({"error": "user_email não encontrado"}, status=400)

        try:
            user = User.objects.get(email=user_email)
            subscription = Subscription.objects.get(user=user)

            subscription.stripe_subscription_id = stripe_subscription_id
            subscription.active = True
            subscription.end_date = timezone.now() + timedelta(days=30)
            subscription.save()

            print(f"✅ Assinatura ativada: {user_email} - {stripe_subscription_id}")
            return JsonResponse({"message": "Assinatura ativada"}, status=200)

        except User.DoesNotExist:
            print(f"❌ Erro: Usuário com e-mail {user_email} não encontrado.")
            return JsonResponse({"error": "Usuário não encontrado"}, status=404)

        except Subscription.DoesNotExist:
            print(f"❌ Erro: Nenhuma assinatura encontrada para {user_email}")
            return JsonResponse({"error": "Assinatura não encontrada"}, status=404)

    elif event_type == "invoice.payment_succeeded":
        stripe_subscription_id = event["data"]["object"]["subscription"]
        try:
            subscription = Subscription.objects.get(stripe_subscription_id=stripe_subscription_id)
            subscription.active = True
            subscription.save()
            print(f"✅ Pagamento confirmado: {subscription.user.email}")
            return JsonResponse({"message": "Pagamento confirmado"}, status=200)
        except Subscription.DoesNotExist:
            print("❌ Erro: Assinatura não encontrada para esse pagamento")
            return JsonResponse({"error": "Assinatura não encontrada"}, status=404)

    print("⚡ Evento Stripe recebido, mas não processado.")
    return JsonResponse({"message": "Evento recebido"}, status=200)