from django.apps import AppConfig
from django.conf import settings
import tensorflow as tf
import os


class WebsiteConfig(AppConfig):
    name = 'website'

    path = os.path.join(settings.MODELS, 'alexnet')
 
    model= tf.keras.models.load_model(path)
