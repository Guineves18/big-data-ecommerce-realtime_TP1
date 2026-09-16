import json
import time
import random
import uuid
from datetime import datetime

# Lista de possíveis eventos em um e-commerce
EVENT_TYPES = ['view_item', 'add_to_cart', 'checkout', 'purchase', 'shipping_update']

# Lista de produtos falsos
PRODUCTS = [
    {'id': 'P001', 'name': 'Smartphone X', 'price': 2999.99},
    {'id': 'P002', 'name': 'Notebook Pro', 'price': 5499.00},
    {'id': 'P003', 'name': 'Fone Bluetooth', 'price': 199.90},
    {'id': 'P004', 'name': 'Smart TV 55', 'price': 3199.50},
    {'id': 'P005', 'name': 'Console Gamer', 'price': 4200.00}
]

# Possíveis status de entrega (apenas para shipping_update)
SHIPPING_STATUSES = ['preparando', 'em_transito', 'saiu_para_entrega', 'entregue']

LOG_FILE = 'ecommerce_events.log'

def generate_event():
    event_type = random.choices(EVENT_TYPES, weights=[50, 20, 10, 5, 15])[0]
    product = random.choice(PRODUCTS)
    
    event = {
        'event_id': str(uuid.uuid4()),
        'user_id': f"U{random.randint(1000, 9999)}",
        'timestamp': datetime.utcnow().isoformat() + "Z",
        'event_type': event_type,
        'product_id': product['id'],
        'price': product['price']
    }

    if event_type == 'shipping_update':
        event['shipping_status'] = random.choice(SHIPPING_STATUSES)
    
    return event

if __name__ == '__main__':
    print(f"Iniciando gerador de eventos. Escrevendo em {LOG_FILE}...")
    with open(LOG_FILE, 'a') as f:
        while True:
            event = generate_event()
            json_str = json.dumps(event)
            f.write(json_str + '\n')
            f.flush()
            
            # Imprime no console também para visualização
            print(json_str)
            
            # Intervalo aleatório entre eventos para simular tráfego
            time.sleep(random.uniform(0.1, 1.5))
