from django.core.management.base import BaseCommand
from core.models import Customer, Supplier, Warehouse, Location, Category, Product
from django.utils import timezone
import random

# Sample data
PAKISTANI_CITIES = [
    ("Karachi", "74200"), ("Lahore", "54000"), ("Islamabad", "44000"), ("Rawalpindi", "46000"),
    ("Faisalabad", "38000"), ("Multan", "60000"), ("Peshawar", "25000"), ("Quetta", "87300"),
    ("Sialkot", "51310"), ("Hyderabad", "71000")
]
MUSLIM_MALE_NAMES = [
    "Ahmed", "Muhammad", "Ali", "Hassan", "Usman", "Bilal", "Imran", "Zain", "Saad", "Hamza"
]
MUSLIM_FEMALE_NAMES = [
    "Ayesha", "Fatima", "Zainab", "Maryam", "Hira", "Sana", "Mariam", "Noor", "Iqra", "Sara"
]
BUSINESS_NAMES = [
    "Al-Falah Traders", "Noor Enterprises", "Siddiq Sons", "Pak Distributors", "Al-Habib Mart",
    "Rehman Supplies", "Safa Traders", "Al-Madina Stores", "Iqbal Agencies", "Hussain & Co."
]
CATEGORY_TITLES = [
    "Beverages", "Snacks", "Dairy", "Bakery", "Personal Care", "Household", "Frozen Foods", "Produce", "Meat", "Spices"
]
PRODUCT_NAMES = [
    "Tea", "Chips", "Milk", "Bread", "Shampoo", "Detergent", "Frozen Peas", "Tomatoes", "Chicken", "Red Chilli Powder"
]

class Command(BaseCommand):
    help = 'Populates the database with sample Customers, Suppliers, Warehouses, Locations, Categories, and Products.'

    def handle(self, *args, **options):
        # Locations
        locations = []
        for i, (city, postcode) in enumerate(PAKISTANI_CITIES):
            loc = Location.objects.create(
                name=f"Warehouse Location {i+1}",
                address=f"{random.randint(1, 100)} Main Road, {city}, Pakistan, {postcode}"
            )
            locations.append(loc)
        self.stdout.write(self.style.SUCCESS(f"Created {len(locations)} Locations."))

        # Warehouses
        warehouses = []
        for i in range(10):
            wh = Warehouse.objects.create(
                name=f"Warehouse {i+1}",
                isRefrigerated=bool(i % 2),
                location=locations[i % len(locations)]
            )
            warehouses.append(wh)
        self.stdout.write(self.style.SUCCESS(f"Created {len(warehouses)} Warehouses."))

        # Categories
        categories = []
        for i, title in enumerate(CATEGORY_TITLES):
            cat = Category.objects.create(
                title=title,
                description=f"Sample category for {title}"
            )
            categories.append(cat)
        self.stdout.write(self.style.SUCCESS(f"Created {len(categories)} Categories."))

        # Customers
        customers = []
        for i in range(10):
            name = random.choice(MUSLIM_MALE_NAMES + MUSLIM_FEMALE_NAMES)
            city, postcode = random.choice(PAKISTANI_CITIES)
            cust = Customer.objects.create(
                email=f"customer{i+1}@example.com",
                name=name,
                telephone=f"03{random.randint(100000000, 999999999)}",
                address_street=f"{random.randint(10, 99)} Street, {city}",
                address_city=city,
                address_postcode=postcode
            )
            customers.append(cust)
        self.stdout.write(self.style.SUCCESS(f"Created {len(customers)} Customers."))

        # Suppliers
        suppliers = []
        for i in range(10):
            first_name = random.choice(MUSLIM_MALE_NAMES)
            last_name = random.choice(["Khan", "Ahmed", "Malik", "Hussain", "Sheikh", "Qureshi", "Raza", "Butt", "Chaudhry", "Siddiqui"])
            business = BUSINESS_NAMES[i % len(BUSINESS_NAMES)]
            city, postcode = random.choice(PAKISTANI_CITIES)
            supp = Supplier.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=f"supplier{i+1}@example.com",
                address_street=f"{random.randint(1, 50)} Market Road, {city}",
                address_city=city,
                address_postcode=postcode,
                telephone=f"03{random.randint(100000000, 999999999)}",
                businessName=business,
                accountNumber=f"PK{random.randint(10000000, 99999999)}"
            )
            suppliers.append(supp)
        self.stdout.write(self.style.SUCCESS(f"Created {len(suppliers)} Suppliers."))

        # Products
        products = []
        for i, pname in enumerate(PRODUCT_NAMES):
            cat = categories[i % len(categories)]
            prod = Product.objects.create(
                barCode=f"PK{random.randint(100000000000, 999999999999)}",
                name=pname,
                description=f"Sample product: {pname}",
                category=cat,
                expiryDate=timezone.now().date(),
                averageCostPrice=random.uniform(50, 500),
                sellingPrice=random.uniform(60, 600),
                packedWeight=random.uniform(0.5, 5.0),
                packedHeight=random.uniform(5, 20),
                packedWidth=random.uniform(5, 20),
                packedDepth=random.uniform(5, 20),
                refrigerated=bool(i % 2)
            )
            # Assign to random warehouses
            prod.warehouses.set(random.sample(warehouses, k=random.randint(1, 3)))
            products.append(prod)
        self.stdout.write(self.style.SUCCESS(f"Created {len(products)} Products."))

        self.stdout.write(self.style.SUCCESS("Sample data population complete!"))
