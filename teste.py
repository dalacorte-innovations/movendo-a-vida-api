import stripe

stripe.api_key = ""

products = stripe.Product.list()

for product in products.data:
    print(f"Produto: {product.name}, ID: {product.id}")


# Produto: Produto Profissional, ID: prod_R4KnQtPfACxxqw
# Produto: Plano Avançado, ID: prod_R4Gur633UlAC4k
# Produto: Plano Iniciante, ID: prod_R4GsHVDvVBhoXN