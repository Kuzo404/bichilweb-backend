import re
import json
from rest_framework import serializers
from django.conf import settings
import cloudinary
import cloudinary.uploader
from app.models.models import Footer, FooterSocials, FooterUrls

cloudinary.config(
    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
)

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
    logo = serializers.FileField(required=False, allow_null=True, write_only=True)
    
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
    
    def _upload_to_cloudinary(self, file_obj):
        """Cloudinary дээр зураг upload хийнэ."""
        name_without_ext = file_obj.name.rsplit('.', 1)[0] if '.' in file_obj.name else file_obj.name
        folder = 'bichil/footer'
        if hasattr(file_obj, 'temporary_file_path'):
            upload_source = file_obj.temporary_file_path()
        else:
            upload_source = file_obj
        result = cloudinary.uploader.upload(
            upload_source,
            resource_type='image',
            folder=folder,
            public_id=name_without_ext,
            overwrite=True,
            quality='auto',
            fetch_format='auto',
        )
        return result['secure_url']

    def _delete_from_cloudinary(self, url):
        """Cloudinary URL-с public_id гаргаж устгана."""
        if not url or 'cloudinary.com' not in str(url):
            return
        try:
            match = re.search(r'/upload/v\d+/(.+)$', url)
            if not match:
                return
            public_id = match.group(1).rsplit('.', 1)[0]
            cloudinary.uploader.destroy(public_id, resource_type='image')
            print(f'✅ Cloudinary footer logo deleted: {public_id}')
        except Exception as e:
            print(f'❌ Cloudinary footer delete error: {e}')
    
    def create(self, validated_data):
        socials_data = validated_data.pop('socials', [])
        urls_data = validated_data.pop('urls', [])
        logo_file = validated_data.pop('logo', None)
        
        if logo_file:
            cloudinary_url = self._upload_to_cloudinary(logo_file)
            validated_data['logo'] = cloudinary_url
            print(f'✅ Footer logo uploaded: {cloudinary_url}')
        
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
                self._delete_from_cloudinary(instance.logo)
            cloudinary_url = self._upload_to_cloudinary(logo_file)
            validated_data['logo'] = cloudinary_url
            print(f'✅ Footer logo updated: {cloudinary_url}')
        
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