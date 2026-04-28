from factory import DjangoModelFactory, Faker
from .models import Movie

class MovieFactory(DjangoModelFactory):
    class Meta:
        model = Movie
    """
    When using faker providers, it will generate random data for each field. 
    The title will randomly generate a sentence of four words and genres 
    to a list of variable-length strings. These definitions ensure 
    that each time you create a new Movie instance with MovieFactory, it will 
    have randomly generated values suitable for testing purposes.
    """
    title = Faker('sentence', nb_words=4)
    genres = Faker('pylist', nb_elements=3,
    variable_nb_elements=True, value_types=['str'])