"""
Factory Boy Data Factories

Provides test data factories using Factory Boy and Faker for generating
realistic test data.
"""

import factory
from faker import Faker

fake = Faker()


class UserFactory(factory.Factory):
    """Factory for generating user data."""
    
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n + 1)
    name = factory.LazyAttribute(lambda _: fake.name())
    username = factory.LazyAttribute(lambda _: fake.user_name())
    email = factory.LazyAttribute(lambda _: fake.email())
    phone = factory.LazyAttribute(lambda _: fake.phone_number())
    website = factory.LazyAttribute(lambda _: fake.domain_name())
    
    # Address
    @factory.lazy_attribute
    def address(self):
        return {
            "street": fake.street_address(),
            "suite": fake.secondary_address(),
            "city": fake.city(),
            "zipcode": fake.zipcode(),
            "geo": {
                "lat": fake.latitude(),
                "lng": fake.longitude()
            }
        }
    
    # Company
    @factory.lazy_attribute
    def company(self):
        return {
            "name": fake.company(),
            "catchPhrase": fake.catch_phrase(),
            "bs": fake.bs()
        }


class PostFactory(factory.Factory):
    """Factory for generating post data."""
    
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n + 1)
    userId = factory.LazyAttribute(lambda _: fake.random_int(min=1, max=10))
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=6))
    body = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=3))


class CommentFactory(factory.Factory):
    """Factory for generating comment data."""
    
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n + 1)
    postId = factory.LazyAttribute(lambda _: fake.random_int(min=1, max=100))
    name = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4))
    email = factory.LazyAttribute(lambda _: fake.email())
    body = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=2))


class TodoFactory(factory.Factory):
    """Factory for generating todo data."""
    
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n + 1)
    userId = factory.LazyAttribute(lambda _: fake.random_int(min=1, max=10))
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=5))
    completed = factory.LazyAttribute(lambda _: fake.boolean())


class AlbumFactory(factory.Factory):
    """Factory for generating album data."""
    
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n + 1)
    userId = factory.LazyAttribute(lambda _: fake.random_int(min=1, max=10))
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4))


class PhotoFactory(factory.Factory):
    """Factory for generating photo data."""
    
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n + 1)
    albumId = factory.LazyAttribute(lambda _: fake.random_int(min=1, max=100))
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=3))
    url = factory.LazyAttribute(lambda _: fake.image_url())
    thumbnailUrl = factory.LazyAttribute(lambda _: fake.image_url(width=150, height=150))


# Batch generation helpers

def generate_users(count: int = 5) -> list:
    """Generate multiple users."""
    return [UserFactory() for _ in range(count)]


def generate_posts(count: int = 10) -> list:
    """Generate multiple posts."""
    return [PostFactory() for _ in range(count)]


def generate_comments(count: int = 10) -> list:
    """Generate multiple comments."""
    return [CommentFactory() for _ in range(count)]


def generate_todos(count: int = 10) -> list:
    """Generate multiple todos."""
    return [TodoFactory() for _ in range(count)]


def generate_albums(count: int = 5) -> list:
    """Generate multiple albums."""
    return [AlbumFactory() for _ in range(count)]


def generate_photos(count: int = 20) -> list:
    """Generate multiple photos."""
    return [PhotoFactory() for _ in range(count)]
