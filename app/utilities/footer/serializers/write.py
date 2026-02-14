from rest_framework import serializers
from app.models.models import Footer, FooterSocials, FooterUrls
import os, json
from django.conf import settings
import uuid

class FooterSocialsWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FooterSocials
        fields = ['social', 'url', 'index', 'active']


class FooterUrlsWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FooterUrls
        fields = ['nameen', 'namemn', 'url']


class FooterWriteSerializer(serializers.ModelSerializer):
    socials = FooterSocialsWriteSerializer(many=True, required=False)
    urls = FooterUrlsWriteSerializer(many=True, required=False)
    logo = serializers.ImageField(required=False, allow_null=True, write_only=True)
    
    class Meta:
        model = Footer
        fields = [
            'logotext',
            'logo',
            'svg',
            'descmn',
            'descen',
            'locationmn',
            'locationen',
            'email',
            'phone',
            'bgcolor',
            'fontcolor',
            'featurecolor',
            'socialiconcolor',
            'titlesize',
            'fontsize',
            'copyrighten',
            'copyrightmn',
            'socials',
            'urls',
        ]

    def to_internal_value(self, data):
        """Parse socials/urls JSON strings from multipart FormData"""
        # Convert QueryDict to a plain dict so DRF doesn't use HTML list parsing
        plain_data = {}
        for key in data:
            if key in ('socials', 'urls'):
                raw = data.get(key)
                if isinstance(raw, str):
                    try:
                        parsed = json.loads(raw)
                        if isinstance(parsed, list):
                            plain_data[key] = parsed
                            continue
                    except (json.JSONDecodeError, TypeError):
                        pass
                plain_data[key] = raw
            elif key == 'logo':
                plain_data[key] = data.get(key)
            else:
                plain_data[key] = data.get(key)
        
        return super().to_internal_value(plain_data)
    
    def _save_image(self, image_file):
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'footer')
        os.makedirs(upload_dir, exist_ok=True)
        
        ext = os.path.splitext(image_file.name)[1].lower()
        filename = f"{uuid.uuid4()}{ext}"
        
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        return filename
    
    def _delete_image(self, filename):
        if filename:
            clean_filename = filename.replace('media/', '').replace('footer/', '')
            image_path = os.path.join(settings.MEDIA_ROOT, 'footer', clean_filename)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"✅ Image deleted: {clean_filename}")
                except Exception as e:
                    print(f"❌ Error deleting image: {e}")
    
    def create(self, validated_data):
        socials_data = validated_data.pop('socials', [])
        urls_data = validated_data.pop('urls', [])
        logo_file = validated_data.pop('logo', None)
        
        if logo_file:
            filename = self._save_image(logo_file)
            validated_data['logo'] = filename
            print(f"✅ Logo saved: {filename}")
        
        footer = Footer.objects.create(**validated_data)
        
        # Create socials
        for social_data in socials_data:
            FooterSocials.objects.create(footer=footer, **social_data)
        
        for url_data in urls_data:
            FooterUrls.objects.create(footer=footer, **url_data)
        
        return footer
    
    def update(self, instance, validated_data):
        socials_data = validated_data.pop('socials', None)
        urls_data = validated_data.pop('urls', None)
        logo_file = validated_data.pop('logo', None)
        
        if logo_file:
            if instance.logo:
                self._delete_image(instance.logo)
            filename = self._save_image(logo_file)
            validated_data['logo'] = filename
            print(f"✅ Logo updated: {filename}")
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if socials_data is not None:
            instance.footersocials_set.all().delete()
            for social_data in socials_data:
                FooterSocials.objects.create(footer=instance, **social_data)
        
        if urls_data is not None:
            instance.footerurls_set.all().delete()
            for url_data in urls_data:
                FooterUrls.objects.create(footer=instance, **url_data)
        
        return instance