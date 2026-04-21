import logging
from django.db import models

logger = logging.getLogger(__name__)
# Create your models here.
class MyModel(models.Model):
    name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        logger.info("Saving MyModel instance: %s", self.name)
        super().save(*args, **kwargs)
        
        if self.name == "bad":
            logger.error("Invalid name detected: %s", self.name)
