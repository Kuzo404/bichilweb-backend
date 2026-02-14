from rest_framework import serializers
from app.models.models import Cta, CtaTitle, CtaSubtitle


class CtaTitleSerializer(serializers.ModelSerializer):
    # ✅ Хэрвээ language нь ForeignKey бол ID-г нь авах
    language_id = serializers.IntegerField(source='language.id', read_only=True)
    
    class Meta:
        model = CtaTitle
        fields = ["id", "language", "language_id", "label"]
    
    def to_representation(self, instance):
        """Custom representation to handle Language object"""
        data = super().to_representation(instance)
        
        # Хэрвээ language нь object бол ID эсвэл value-г нь авах
        if hasattr(instance.language, 'id'):
            data['language'] = instance.language.id
        elif hasattr(instance.language, 'pk'):
            data['language'] = instance.language.pk
        
        # language_id field-ийг устгах (optional)
        data.pop('language_id', None)
        
        return data


class CtaSubtitleSerializer(serializers.ModelSerializer):
    # ✅ Хэрвээ language нь ForeignKey бол ID-г нь авах
    language_id = serializers.IntegerField(source='language.id', read_only=True)
    
    class Meta:
        model = CtaSubtitle
        fields = ["id", "language", "language_id", "label"]
    
    def to_representation(self, instance):
        """Custom representation to handle Language object"""
        data = super().to_representation(instance)
        
        # Хэрвээ language нь object бол ID эсвэл value-г нь авах
        if hasattr(instance.language, 'id'):
            data['language'] = instance.language.id
        elif hasattr(instance.language, 'pk'):
            data['language'] = instance.language.pk
        
        # language_id field-ийг устгах (optional)
        data.pop('language_id', None)
        
        return data


class CtaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    titles = serializers.SerializerMethodField()
    subtitles = serializers.SerializerMethodField()

    class Meta:
        model = Cta
        fields = [
            "id",
            "file",
            "file_url",
            "index",
            "font",
            "color",
            "number",
            "description",
            "url",
            "titles",
            "subtitles",
        ]

    def get_file_url(self, obj):
        """Return full URL for file"""
        if obj.file:
            # Remove 'media/' prefix if it exists
            file_path = obj.file.replace('media/', '')
            return f'/media/{file_path}'
        return None

    def get_titles(self, obj):
        """Return titles list with language ID"""
        titles = []
        for t in obj.ctatitle_set.all():
            # ✅ Language object-ийг ID болгон хувиргах
            language_value = t.language
            if hasattr(language_value, 'id'):
                language_value = language_value.id
            elif hasattr(language_value, 'pk'):
                language_value = language_value.pk
            
            titles.append({
                "id": t.id,
                "language": language_value,
                "label": t.label
            })
        return titles

    def get_subtitles(self, obj):
        """Return subtitles list with language ID"""
        subtitles = []
        for s in obj.ctasubtitle_set.all():
            # ✅ Language object-ийг ID болгон хувиргах
            language_value = s.language
            if hasattr(language_value, 'id'):
                language_value = language_value.id
            elif hasattr(language_value, 'pk'):
                language_value = language_value.pk
            
            subtitles.append({
                "id": s.id,
                "language": language_value,
                "label": s.label
            })
        return subtitles


# =============================================================================
# ALTERNATIVE APPROACH - Using nested serializers
# =============================================================================

class CtaSerializerAlternative(serializers.ModelSerializer):
    """Alternative approach using nested serializers"""
    file_url = serializers.SerializerMethodField()
    titles = CtaTitleSerializer(source='ctatitle_set', many=True, read_only=True)
    subtitles = CtaSubtitleSerializer(source='ctasubtitle_set', many=True, read_only=True)

    class Meta:
        model = Cta
        fields = [
            "id",
            "file",
            "file_url",
            "index",
            "font",
            "color",
            "number",
            "description",
            "url",
            "titles",
            "subtitles",
        ]

    def get_file_url(self, obj):
        if obj.file:
            file_path = obj.file.replace('media/', '')
            return f'/media/{file_path}'
        return None

