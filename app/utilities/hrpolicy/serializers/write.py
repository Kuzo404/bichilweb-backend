from rest_framework import serializers
from app.models.models import HrPolicy, HrPolicyTranslations

class HrPolicyTranslationsWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = HrPolicyTranslations
        fields = ('language', 'name', 'desc')


class HrPolicyWriteSerializer(serializers.ModelSerializer):
    translations = HrPolicyTranslationsWriteSerializer(many=True)
    
    class Meta:
        model = HrPolicy
        fields = (
            'id', 'key', 'visual_type', 'visual_preset', 'font_color',
            'bg_color', 'fontsize', 'active', 'translations'
        )
        extra_kwargs = {
            'key': {'required': True},
            'active': {'required': False, 'default': True}
        }
    
    def create(self, validated_data):
        from django.utils import timezone
        translations_data = validated_data.pop('translations', [])
        validated_data['created_at'] = timezone.now()
        
        policy = HrPolicy.objects.create(**validated_data)
        
        for translation_data in translations_data:
            HrPolicyTranslations.objects.create(
                policy=policy,
                **translation_data
            )
        
        return policy
    
    def update(self, instance, validated_data):
        translations_data = validated_data.pop('translations', None)
        
        for field in ['key', 'visual_type', 'visual_preset', 'font_color', 
                      'bg_color', 'fontsize', 'active']:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        
        instance.save()
        
        if translations_data is not None:
            instance.hrpolicytranslations_set.all().delete()
            
            for translation_data in translations_data:
                HrPolicyTranslations.objects.create(
                    policy=instance,
                    **translation_data
                )
        
        return instance