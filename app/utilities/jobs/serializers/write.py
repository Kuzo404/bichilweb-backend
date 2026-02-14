from rest_framework import serializers
from app.models.models import Jobs, JobTranslations

class JobTranslationWriteSerializer(serializers.Serializer):
    language = serializers.IntegerField()
    title = serializers.CharField()
    department = serializers.CharField()
    desc = serializers.CharField()
    requirements = serializers.CharField(allow_blank=True, allow_null=True, required=False)


class JobWriteSerializer(serializers.Serializer):
    type = serializers.IntegerField()
    location = serializers.CharField()
    deadline = serializers.DateField()
    status = serializers.IntegerField()
    translations = JobTranslationWriteSerializer(many=True)
    
    def validate_translations(self, value):
        """Validate that we have at least one translation"""
        if not value:
            raise serializers.ValidationError("At least one translation is required")
        
        languages = [t['language'] for t in value]
        if len(languages) != len(set(languages)):
            raise serializers.ValidationError("Duplicate languages are not allowed")
        
        return value
    
    def create(self, validated_data):
        """Create job with translations"""
        from django.utils import timezone
        
        translations_data = validated_data.pop('translations')
        
        job = Jobs.objects.create(
            type=validated_data['type'],
            location=validated_data['location'],
            deadline=validated_data['deadline'],
            status=validated_data['status'],
            date=timezone.now()
        )
        
        for translation_data in translations_data:
            JobTranslations.objects.create(
                job=job,
                language_id=translation_data['language'],
                title=translation_data['title'],
                department=translation_data['department'],
                desc=translation_data['desc'],
                requirements=translation_data.get('requirements', '')
            )
        
        return job
    
    def update(self, instance, validated_data):
        
        translations_data = validated_data.pop('translations', None)
        
        instance.type = validated_data.get('type', instance.type)
        instance.location = validated_data.get('location', instance.location)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        if translations_data is not None:
            JobTranslations.objects.filter(job=instance).delete()
            
            for translation_data in translations_data:
                JobTranslations.objects.create(
                    job=instance,
                    language_id=translation_data['language'],
                    title=translation_data['title'],
                    department=translation_data['department'],
                    desc=translation_data['desc'],
                    requirements=translation_data.get('requirements', '')
                )
        
        return instance