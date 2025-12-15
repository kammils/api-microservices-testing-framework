"""
Factory Boy Factories Module

Provides factories for generating test data using Factory Boy and Faker.
"""

from datetime import datetime
from typing import Any, Dict

import factory
from factory import Faker, LazyAttribute, Sequence
from faker import Faker as FakerInstance

from src.config import get_config

# Get faker configuration
config = get_config()
fake = FakerInstance(config.faker_locale)

if config.faker_seed:
    Faker._DEFAULT_LOCALE = config.faker_locale
    factory.Faker._DEFAULT_LOCALE = config.faker_locale


class UserFactory(factory.Factory):
    """Factory for generating user test data"""

    class Meta:
        model = dict

    id = Sequence(lambda n: n + 1)
    username = Faker("user_name")
    email = Faker("email")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    password = LazyAttribute(lambda x: fake.password(length=12))
    age = Faker("random_int", min=18, max=80)
    phone = Faker("phone_number")
    address = Faker("address")
    city = Faker("city")
    country = Faker("country")
    is_active = True
    created_at = LazyAttribute(lambda x: datetime.now().isoformat())
    updated_at = LazyAttribute(lambda x: datetime.now().isoformat())

    @classmethod
    def create_batch_dict(cls, size: int, **kwargs) -> list[Dict[str, Any]]:
        """Create a batch of users"""
        return [cls(**kwargs) for _ in range(size)]


class ProductFactory(factory.Factory):
    """Factory for generating product test data"""

    class Meta:
        model = dict

    id = Sequence(lambda n: n + 1)
    name = Faker("catch_phrase")
    description = Faker("text", max_nb_chars=200)
    price = Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    category = Faker(
        "random_element", elements=["Electronics", "Clothing", "Books", "Food", "Home"]
    )
    sku = LazyAttribute(lambda x: fake.bothify(text="SKU-####-????").upper())
    stock_quantity = Faker("random_int", min=0, max=1000)
    manufacturer = Faker("company")
    is_available = True
    created_at = LazyAttribute(lambda x: datetime.now().isoformat())
    updated_at = LazyAttribute(lambda x: datetime.now().isoformat())

    @classmethod
    def create_batch_dict(cls, size: int, **kwargs) -> list[Dict[str, Any]]:
        """Create a batch of products"""
        return [cls(**kwargs) for _ in range(size)]


class OrderFactory(factory.Factory):
    """Factory for generating order test data"""

    class Meta:
        model = dict

    id = Sequence(lambda n: n + 1)
    order_number = LazyAttribute(lambda x: fake.bothify(text="ORD-########"))
    user_id = Faker("random_int", min=1, max=1000)
    product_id = Faker("random_int", min=1, max=1000)
    quantity = Faker("random_int", min=1, max=10)
    unit_price = Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    total_price = LazyAttribute(lambda o: float(o.unit_price) * o.quantity)
    status = Faker(
        "random_element",
        elements=["pending", "processing", "shipped", "delivered", "cancelled"],
    )
    shipping_address = Faker("address")
    payment_method = Faker("random_element", elements=["credit_card", "debit_card", "paypal", "cash"])
    created_at = LazyAttribute(lambda x: datetime.now().isoformat())
    updated_at = LazyAttribute(lambda x: datetime.now().isoformat())

    @classmethod
    def create_batch_dict(cls, size: int, **kwargs) -> list[Dict[str, Any]]:
        """Create a batch of orders"""
        return [cls(**kwargs) for _ in range(size)]


class APIRequestFactory(factory.Factory):
    """Factory for generating API request test data"""

    class Meta:
        model = dict

    endpoint = Faker("uri_path")
    method = Faker("random_element", elements=["GET", "POST", "PUT", "PATCH", "DELETE"])
    headers = LazyAttribute(
        lambda x: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": fake.user_agent(),
        }
    )
    query_params = LazyAttribute(
        lambda x: {"page": fake.random_int(1, 10), "limit": fake.random_int(10, 100)}
    )


class ErrorResponseFactory(factory.Factory):
    """Factory for generating error response test data"""

    class Meta:
        model = dict

    error = True
    status_code = Faker("random_element", elements=[400, 401, 403, 404, 500, 502, 503])
    message = Faker("sentence")
    error_code = LazyAttribute(lambda x: f"ERR_{fake.random_int(1000, 9999)}")
    timestamp = LazyAttribute(lambda x: datetime.now().isoformat())
    details = LazyAttribute(lambda x: {"field": fake.word(), "reason": fake.sentence()})


# Convenience functions for quick data generation
def generate_user(**overrides) -> Dict[str, Any]:
    """Generate a single user"""
    return UserFactory(**overrides)


def generate_users(count: int = 5, **overrides) -> list[Dict[str, Any]]:
    """Generate multiple users"""
    return UserFactory.create_batch_dict(count, **overrides)


def generate_product(**overrides) -> Dict[str, Any]:
    """Generate a single product"""
    return ProductFactory(**overrides)


def generate_products(count: int = 5, **overrides) -> list[Dict[str, Any]]:
    """Generate multiple products"""
    return ProductFactory.create_batch_dict(count, **overrides)


def generate_order(**overrides) -> Dict[str, Any]:
    """Generate a single order"""
    return OrderFactory(**overrides)


def generate_orders(count: int = 5, **overrides) -> list[Dict[str, Any]]:
    """Generate multiple orders"""
    return OrderFactory.create_batch_dict(count, **overrides)
