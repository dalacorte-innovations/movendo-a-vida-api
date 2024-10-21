import stripe

stripe.api_key = "sk_test_51QC5ZZG6OUsgFCnIsZ8gx2GhFLV7DRkVqiICYnQTv9wqnnfEnqridcE8YLmBgkZc75882aokgg0fjK0CYl0CkCa2005doe9Nl2"

products = stripe.Product.list()

# Para cada produto, listar os preços (prices) associados
for product in products.data:
    print(f"Produto: {product.name}, ID: {product.id}")

    # Listar os preços do produto
    prices = stripe.Price.list(product=product.id)
    
    for price in prices.data:
        print(f"  Preço ID: {price.id}, Valor: {price.unit_amount / 100} {price.currency}, Recorrência: {price.recurring}")

# price_1QCC7VG6OUsgFCnIJ8AHK9tK 200
# price_1QC8MZG6OUsgFCnItOWh03Tz 100
# price_1QC8KfG6OUsgFCnI2hLU7KE6 59