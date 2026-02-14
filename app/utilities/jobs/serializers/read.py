from rest_framework import serializers
from app.models.models import Jobs, JobTranslations

class JobTranslationReadSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    language = serializers.IntegerField(source='language_id')
    language_code = serializers.CharField(source='language.lang_code', read_only=True)
    language_name = serializers.CharField(source='language.lang_name', read_only=True)
    title = serializers.CharField()
    department = serializers.CharField()
    desc = serializers.CharField()
    requirements = serializers.CharField(allow_blank=True, allow_null=True)


class JobReadSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()
    
    class Meta:
        model = Jobs
        fields = [
            'id',
            'type',
            'location',
            'deadline',
            'status',
            'date',
            'translations'
        ]
    
    def get_translations(self, obj):
        translations = JobTranslations.objects.filter(job=obj).select_related('language')
        return JobTranslationReadSerializer(translations, many=True).data

