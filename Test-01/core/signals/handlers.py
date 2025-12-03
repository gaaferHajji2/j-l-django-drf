from django.dispatch import receiver
from store.signals import order_created

@receiver(order_created) # type: ignore
def order_created(sender, **kwargs):
    print(kwargs['order'])