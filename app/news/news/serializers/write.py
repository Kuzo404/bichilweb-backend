from rest_framework import serializers
from app.models.models import (
    News,
    NewsImages,
    NewsSocials,
    NewsTitleTranslations,
    NewsShortdescTranslations,
    NewsContentTranslations,
    Language  # Import Language model
)
import json
import os
from django.conf import settings
import uuid


class NewsWriteSerializer(serializers.ModelSerializer):
    # Nested data as JSON strings
    images = serializers.CharField(write_only=True, required=False, allow_blank=True)
    socials = serializers.CharField(write_only=True, required=False, allow_blank=True)
    title_translations = serializers.CharField(write_only=True)
    shortdesc_translations = serializers.CharField(write_only=True)
    content_translations = serializers.CharField(write_only=True)
    
    # Main image file
    image = serializers.ImageField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = News
        fields = (
            "id",
            "category",
            "image",
            "video",
            "feature",
            "render",
            "show_on_home",
            "readtime",
            "slug",
            "date",
            "images",
            "socials",
            "title_translations",
            "shortdesc_translations",
            "content_translations"
        )

    def validate_images(self, value):
        """Validate images JSON string"""
        if not value or value.strip() == '':
            return []
        try:
            data = json.loads(value) if isinstance(value, str) else value
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for images")

    def validate_socials(self, value):
        """Validate socials JSON string"""
        if not value or value.strip() == '':
            return []
        try:
            data = json.loads(value) if isinstance(value, str) else value
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for socials")

    def validate_title_translations(self, value):
        """Validate title translations JSON string"""
        try:
            data = json.loads(value) if isinstance(value, str) else value
            if not isinstance(data, list) or not data:
                raise serializers.ValidationError("Title translations must be a non-empty list")
            return data
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for title_translations")

    def validate_shortdesc_translations(self, value):
        """Validate shortdesc translations JSON string"""
        try:
            data = json.loads(value) if isinstance(value, str) else value
            if not isinstance(data, list) or not data:
                raise serializers.ValidationError("Shortdesc translations must be a non-empty list")
            return data
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for shortdesc_translations")

    def validate_content_translations(self, value):
        """Validate content translations JSON string"""
        try:
            data = json.loads(value) if isinstance(value, str) else value
            if not isinstance(data, list) or not data:
                raise serializers.ValidationError("Content translations must be a non-empty list")
            return data
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for content_translations")

    def _save_image(self, image_file):
        """Save image and return filename"""
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'news')
        os.makedirs(upload_dir, exist_ok=True)
        
        ext = os.path.splitext(image_file.name)[1].lower()
        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(upload_dir, filename)
        
        with open(filepath, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        return filename

    def _delete_image(self, filename):
        """Delete old image"""
        if filename:
            clean_filename = filename.replace('media/', '').replace('news/', '')
            image_path = os.path.join(settings.MEDIA_ROOT, 'news', clean_filename)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"✅ Image deleted: {clean_filename}")
                except Exception as e:
                    print(f"❌ Error deleting image: {e}")

    def _get_language_instance(self, language_id):
        """Get Language instance by ID"""
        try:
            return Language.objects.get(id=language_id)
        except Language.DoesNotExist:
            raise serializers.ValidationError(f"Language with id {language_id} does not exist")

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        socials_data = validated_data.pop('socials', [])
        print(f"📥 SOCIALS DATA in create: {socials_data}")
        title_translations_data = validated_data.pop('title_translations')
        shortdesc_translations_data = validated_data.pop('shortdesc_translations')
        content_translations_data = validated_data.pop('content_translations')
        
        image_file = validated_data.pop('image', None)

        # Save main image
        if image_file:
            filename = self._save_image(image_file)
            validated_data['image'] = filename
            print(f"✅ News image saved: {filename}")

        # Create news
        news = News.objects.create(**validated_data)

        # Create related objects - Images
        for image_data in images_data:
            NewsImages.objects.create(news=news, **image_data)

        # Create related objects - Socials
        for social_data in socials_data:
            NewsSocials.objects.create(news=news, **social_data)

        # Create related objects - Title Translations
        for title_data in title_translations_data:
            language_id = title_data.pop('language')
            language_instance = self._get_language_instance(language_id)
            NewsTitleTranslations.objects.create(
                news=news,
                language=language_instance,
                **title_data
            )

        # Create related objects - Shortdesc Translations
        for shortdesc_data in shortdesc_translations_data:
            language_id = shortdesc_data.pop('language')
            language_instance = self._get_language_instance(language_id)
            NewsShortdescTranslations.objects.create(
                news=news,
                language=language_instance,
                **shortdesc_data
            )

        # Create related objects - Content Translations
        for content_data in content_translations_data:
            language_id = content_data.pop('language')
            language_instance = self._get_language_instance(language_id)
            NewsContentTranslations.objects.create(
                news=news,
                language=language_instance,
                **content_data
            )

        return news

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        socials_data = validated_data.pop('socials', None)
        print(f"📥 SOCIALS DATA in update: {socials_data}")
        title_translations_data = validated_data.pop('title_translations', None)
        shortdesc_translations_data = validated_data.pop('shortdesc_translations', None)
        content_translations_data = validated_data.pop('content_translations', None)
        
        image_file = validated_data.pop('image', None)

        # Update main image
        if image_file:
            # Delete old image
            if instance.image:
                self._delete_image(instance.image)
            
            # Save new image
            filename = self._save_image(image_file)
            validated_data['image'] = filename
            print(f"✅ News image updated: {filename}")

        # Update news fields
        instance.category = validated_data.get('category', instance.category)
        instance.video = validated_data.get('video', instance.video)
        instance.feature = validated_data.get('feature', instance.feature)
        instance.render = validated_data.get('render', instance.render)
        instance.show_on_home = validated_data.get('show_on_home', instance.show_on_home)
        instance.readtime = validated_data.get('readtime', instance.readtime)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.date = validated_data.get('date', instance.date)
        
        # Update image if changed
        if 'image' in validated_data:
            instance.image = validated_data['image']
        
        instance.save()

        # Update related objects - Images
        if images_data is not None:
            instance.newsimages_set.all().delete()
            for image_data in images_data:
                NewsImages.objects.create(news=instance, **image_data)

        # Update related objects - Socials
        if socials_data is not None:
            instance.newssocials_set.all().delete()
            for social_data in socials_data:
                NewsSocials.objects.create(news=instance, **social_data)

        # Update related objects - Title Translations
        if title_translations_data is not None:
            instance.newstitletranslations_set.all().delete()
            for title_data in title_translations_data:
                language_id = title_data.pop('language')
                language_instance = self._get_language_instance(language_id)
                NewsTitleTranslations.objects.create(
                    news=instance,
                    language=language_instance,
                    **title_data
                )

        # Update related objects - Shortdesc Translations
        if shortdesc_translations_data is not None:
            instance.newsshortdesctranslations_set.all().delete()
            for shortdesc_data in shortdesc_translations_data:
                language_id = shortdesc_data.pop('language')
                language_instance = self._get_language_instance(language_id)
                NewsShortdescTranslations.objects.create(
                    news=instance,
                    language=language_instance,
                    **shortdesc_data
                )

        # Update related objects - Content Translations
        if content_translations_data is not None:
            instance.newscontenttranslations_set.all().delete()
            for content_data in content_translations_data:
                language_id = content_data.pop('language')
                language_instance = self._get_language_instance(language_id)
                NewsContentTranslations.objects.create(
                    news=instance,
                    language=language_instance,
                    **content_data
                )

        return instance