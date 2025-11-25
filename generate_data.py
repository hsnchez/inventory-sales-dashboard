# -*- coding: utf-8 -*-
"""
Script to generate synthetic data for an E-commerce in multiple languages.

This script creates two sets of data (English and Spanish) with the SAME schema
(filenames and column headers) but localized content.
Output folders:
- output/en_EN/
- output/es_ES/
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import date, timedelta
import os

# --- CONFIGURATION ---
N_PRODUCTS = 200
START_DATE = date(2022, 1, 1)
SIMULATION_DAYS = 365 * 2
INITIAL_STOCK_MIN = 20
INITIAL_STOCK_MAX = 100
REORDER_THRESHOLD = 15
REORDER_QUANTITY = 50
DAILY_SALE_PROBABILITY = 0.3

# --- LOCALIZED DATA ---
# Dictionary defining content for each language
LOCALIZED_CONTENT = {
    'en_US': {
        'folder': 'en_EN',
        'channels': ['Shopify', 'Amazon', 'Physical Store'],
        'categories': ['Electronics', 'Home', 'Clothing', 'Toys', 'Sports', 'Books'],
        'movement_types': {'initial': 'Initial_Purchase', 'sale': 'Sale', 'purchase': 'Purchase'},
        # Product templates per category to ensure names make sense
        'products_by_category': {
            'Electronics': ['Smartphone', 'Laptop', 'Headphones', 'Smart Watch', 'Tablet', 'Monitor', 'Keyboard', 'Mouse', 'Camera', 'Speaker'],
            'Home': ['Lamp', 'Chair', 'Table', 'Sofa', 'Rug', 'Curtains', 'Cushion', 'Vase', 'Mirror', 'Clock'],
            'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Dress', 'Sweater', 'Shorts', 'Skirt', 'Coat', 'Scarf', 'Hat'],
            'Toys': ['Action Figure', 'Doll', 'Puzzle', 'Board Game', 'Teddy Bear', 'Lego Set', 'Toy Car', 'Drone', 'Kite', 'Ball'],
            'Sports': ['Yoga Mat', 'Dumbbell', 'Tennis Racket', 'Soccer Ball', 'Running Shoes', 'Backpack', 'Water Bottle', 'Helmet', 'Gloves', 'Jersey'],
            'Books': ['Novel', 'Biography', 'Cookbook', 'Textbook', 'Comic', 'Magazine', 'Guide', 'Dictionary', 'Atlas', 'Journal']
        },
        'adjectives': ['Pro', 'Lite', 'Max', 'Ultra', 'Classic', 'Modern', 'Vintage', 'Premium', 'Basic', 'Super'],
        'month_names': {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
    },
    'es_ES': {
        'folder': 'es_ES',
        'channels': ['Shopify', 'MercadoLibre', 'Tienda Física'],
        'categories': ['Electrónica', 'Hogar', 'Ropa', 'Juguetes', 'Deportes', 'Libros'],
        'movement_types': {'initial': 'Compra_Inicial', 'sale': 'Venta', 'purchase': 'Compra'},
        'products_by_category': {
            'Electrónica': ['Smartphone', 'Laptop', 'Auriculares', 'Reloj Inteligente', 'Tablet', 'Monitor', 'Teclado', 'Ratón', 'Cámara', 'Altavoz'],
            'Hogar': ['Lámpara', 'Silla', 'Mesa', 'Sofá', 'Alfombra', 'Cortinas', 'Cojín', 'Jarrón', 'Espejo', 'Reloj'],
            'Ropa': ['Camiseta', 'Jeans', 'Chaqueta', 'Vestido', 'Suéter', 'Pantalones', 'Falda', 'Abrigo', 'Bufanda', 'Sombrero'],
            'Juguetes': ['Figura de Acción', 'Muñeca', 'Rompecabezas', 'Juego de Mesa', 'Oso de Peluche', 'Set de Construcción', 'Coche de Juguete', 'Dron', 'Cometa', 'Pelota'],
            'Deportes': ['Esterilla Yoga', 'Mancuerna', 'Raqueta Tenis', 'Balón Fútbol', 'Zapatillas Running', 'Mochila', 'Botella Agua', 'Casco', 'Guantes', 'Camiseta Deportiva'],
            'Libros': ['Novela', 'Biografía', 'Libro de Cocina', 'Libro de Texto', 'Cómic', 'Revista', 'Guía', 'Diccionario', 'Atlas', 'Diario']
        },
        'adjectives': ['Pro', 'Lite', 'Max', 'Ultra', 'Clásico', 'Moderno', 'Vintage', 'Premium', 'Básico', 'Súper'],
        'month_names': {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
    }
}

def generate_product_name(category, locale_data):
    """Generates a product name that makes sense for the category."""
    base_name = random.choice(locale_data['products_by_category'][category])
    adjective = random.choice(locale_data['adjectives'])
    # 50% chance of having an adjective
    if random.random() > 0.5:
        return f"{base_name} {adjective}"
    return base_name

def generate_dataset(locale, config):
    print(f"\n--- Generating dataset for: {locale} ---")
    fake = Faker(locale)
    
    output_dir = os.path.join('output', config['folder'])
    os.makedirs(output_dir, exist_ok=True)

    # --- 1. DIMENSIONS ---
    
    # Dim_Products
    print("Generating Dim_Products...")
    products_data = []
    for i in range(1, N_PRODUCTS + 1):
        sku = f'SKU-{i:04d}'
        category = random.choice(config['categories'])
        name = generate_product_name(category, config)
        
        cost = round(random.uniform(5.0, 150.0), 2)
        sale_price = round(cost * random.uniform(1.5, 2.5), 2)
        products_data.append([sku, name, category, cost, sale_price])

    dim_products = pd.DataFrame(products_data, columns=['Product_ID', 'Product_Name', 'Category', 'Product_Cost', 'Sale_Price'])

    # Dim_Channels
    print("Generating Dim_Channels...")
    channels_data = [[i+1, name] for i, name in enumerate(config['channels'])]
    dim_channels = pd.DataFrame(channels_data, columns=['Channel_ID', 'Channel_Name'])

    # Dim_Dates
    print("Generating Dim_Dates...")
    date_range = pd.date_range(START_DATE, periods=SIMULATION_DAYS, freq='D')
    
    dates_data = []
    for d in date_range:
        date_str = d.strftime('%Y-%m-%d')
        dates_data.append([
            date_str,
            d.year,
            d.month,
            d.day,
            config['month_names'][d.month], # Correct localized month name
            d.quarter
        ])
        
    dim_dates = pd.DataFrame(dates_data, columns=['Date', 'Year', 'Month', 'Day', 'Month_Name', 'Quarter'])

    # --- 2. FACTS ---
    print("Simulating Sales and Inventory...")
    sales_records = []
    movements_records = []
    sale_id_counter = 1
    movement_id_counter = 1

    current_inventory = {
        sku: random.randint(INITIAL_STOCK_MIN, INITIAL_STOCK_MAX)
        for sku in dim_products['Product_ID']
    }

    # Initial Stock Movements
    initial_date_str = (START_DATE - timedelta(days=1)).strftime('%Y-%m-%d')
    for sku, quantity in current_inventory.items():
        movements_records.append([
            movement_id_counter,
            initial_date_str,
            sku,
            config['movement_types']['initial'],
            quantity
        ])
        movement_id_counter += 1

    # Daily Simulation
    for current_date in dim_dates['Date']:
        # current_date is now a string 'YYYY-MM-DD' from the dataframe
        for _, product in dim_products.iterrows():
            sku = product['Product_ID']

            # Sales
            if random.random() < DAILY_SALE_PROBABILITY:
                quantity_sold = random.randint(1, 5)

                if current_inventory[sku] >= quantity_sold:
                    channel_id = random.choice(dim_channels['Channel_ID'])
                    total_sale = round(quantity_sold * product['Sale_Price'], 2)
                    
                    sales_records.append([
                        sale_id_counter,
                        current_date,
                        sku,
                        channel_id,
                        quantity_sold,
                        product['Sale_Price'],
                        product['Product_Cost'],
                        total_sale
                    ])
                    sale_id_counter += 1

                    movements_records.append([
                        movement_id_counter,
                        current_date,
                        sku,
                        config['movement_types']['sale'],
                        quantity_sold # Absolute value
                    ])
                    movement_id_counter += 1
                    current_inventory[sku] -= quantity_sold

            # Reorder
            if current_inventory[sku] < REORDER_THRESHOLD:
                movements_records.append([
                    movement_id_counter,
                    current_date,
                    sku,
                    config['movement_types']['purchase'],
                    REORDER_QUANTITY
                ])
                movement_id_counter += 1
                current_inventory[sku] += REORDER_QUANTITY

    # --- 3. EXPORT ---
    print(f"Exporting to {output_dir}...")
    
    # Define headers in Spanish (Original Schema) for BOTH datasets to allow seamless PBI switching
    # Dim_Productos
    dim_products.columns = ['ID_Producto', 'Nombre_Producto', 'Categoria', 'Costo_Producto', 'Precio_Venta']
    
    # Dim_Canales
    dim_channels.columns = ['ID_Canal', 'Nombre_Canal']
    
    # Dim_Fechas
    dim_dates.columns = ['Fecha', 'Año', 'Mes', 'Dia', 'Nombre_Mes', 'Trimestre']
    
    # Fact_Ventas
    fact_sales = pd.DataFrame(sales_records, columns=[
        'ID_Venta', 'Fecha', 'ID_Producto', 'ID_Canal', 'Cantidad_Vendida',
        'Precio_Unitario', 'Costo_Unitario', 'Total_Venta'
    ])

    # Fact_Movimientos
    fact_movements = pd.DataFrame(movements_records, columns=[
        'ID_Movimiento', 'Fecha', 'ID_Producto', 'Tipo_Movimiento', 'Cantidad'
    ])

    dim_products.to_csv(os.path.join(output_dir, 'dim_products.csv'), index=False)
    dim_channels.to_csv(os.path.join(output_dir, 'dim_channels.csv'), index=False)
    dim_dates.to_csv(os.path.join(output_dir, 'dim_dates.csv'), index=False)
    fact_sales.to_csv(os.path.join(output_dir, 'fact_sales.csv'), index=False)
    fact_movements.to_csv(os.path.join(output_dir, 'fact_inventory_movements.csv'), index=False)
    
    print(f"Done. Products: {len(dim_products)}, Sales: {len(fact_sales)}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("Starting Multi-Language Data Generation...")
    
    # Generate English Data
    generate_dataset('en_US', LOCALIZED_CONTENT['en_US'])
    
    # Generate Spanish Data
    generate_dataset('es_ES', LOCALIZED_CONTENT['es_ES'])
    
    print("\nAll processes completed successfully!")
