from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from store.models import Customer

# sender: who sent the event to create the new customer
# in our case it is core.models.User
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_new_customer_for_registered_user(sender, **kwargs):
    if kwargs['created']:
        Customer.objects.create(user=kwargs['instance'])