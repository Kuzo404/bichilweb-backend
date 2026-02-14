from rest_framework import serializers
from app.models.models import HeroSlider
from django.conf import settings

class HeroSliderSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    tablet_file_url = serializers.SerializerMethodField()
    mobile_file_url = serializers.SerializerMethodField()

    class Meta:
        model = HeroSlider
        fields = "__all__" 
        

    def get_file_url(self, obj):
        if obj.file:
            return self.context['request'].build_absolute_uri('/' + obj.file)
        return None

    def get_tablet_file_url(self, obj):
        if obj.tablet_file:
            return self.context['request'].build_absolute_uri('/' + obj.tablet_file)
        return None

    def get_mobile_file_url(self, obj):
        if obj.mobile_file:
            return self.context['request'].build_absolute_uri('/' + obj.mobile_file)
        return None
