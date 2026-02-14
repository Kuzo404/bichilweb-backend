from rest_framework import serializers
from app.models.models import AppDownload, AppDownloadTitle, AppDownloadList
import json


class AppDownloadTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppDownloadTitle
        fields = ['id', 'index', 'labelmn', 'labelen', 'color', 'fontsize', 'fontweight', 'top', 'left', 'rotate', 'size']


class AppDownloadListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppDownloadList
        fields = ['id', 'index', 'labelmn', 'labelen', 'icon', 'icon_url']


class AppDownloadReadSerializer(serializers.ModelSerializer):
    titles = AppDownloadTitleSerializer(many=True, read_only=True)
    lists = AppDownloadListItemSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = AppDownload
        fields = [
            'id', 'image', 'image_url', 'index', 'appstore', 'playstore',
            'bgcolor', 'fontcolor', 'titlecolor', 'iconcolor',
            'buttonbgcolor', 'buttonfontcolor',
            'googlebuttonbgcolor', 'googlebuttonfontcolor',
            'active', 'layout', 'features_layout',
            'titles', 'lists',
        ]

    def get_image_url(self, obj):
        if obj.image:
            return f'/media/app_download/{obj.image}'
        return None


class AppDownloadWriteSerializer(serializers.ModelSerializer):
    titles = AppDownloadTitleSerializer(many=True, required=False)
    lists = AppDownloadListItemSerializer(many=True, required=False)
    image_file = serializers.ImageField(required=False, write_only=True)

    class Meta:
        model = AppDownload
        fields = [
            'id', 'image', 'index', 'appstore', 'playstore',
            'bgcolor', 'fontcolor', 'titlecolor', 'iconcolor',
            'buttonbgcolor', 'buttonfontcolor',
            'googlebuttonbgcolor', 'googlebuttonfontcolor',
            'active', 'layout', 'features_layout',
            'titles', 'lists', 'image_file',
        ]

    def to_internal_value(self, data):
        import django.http
        if isinstance(data, django.http.QueryDict):
            plain = {}
            for key in data:
                if key in ('titles', 'lists'):
                    raw = data.get(key)
                    if isinstance(raw, str):
                        try:
                            parsed = json.loads(raw)
                            if isinstance(parsed, list):
                                plain[key] = parsed
                                continue
                        except (json.JSONDecodeError, TypeError):
                            pass
                    plain[key] = raw
                elif key == 'image_file':
                    plain[key] = data.get(key)
                else:
                    plain[key] = data.get(key)
            return super().to_internal_value(plain)
        return super().to_internal_value(data)

    def _save_image(self, instance, request=None):
        import os, uuid
        if request and request.FILES.get('image_file'):
            file = request.FILES['image_file']
            ext = os.path.splitext(file.name)[1]
            filename = f"{uuid.uuid4()}{ext}"
            media_dir = os.path.join('media', 'app_download')
            os.makedirs(media_dir, exist_ok=True)
            filepath = os.path.join(media_dir, filename)
            with open(filepath, 'wb+') as dest:
                for chunk in file.chunks():
                    dest.write(chunk)
            if instance.image:
                old_path = os.path.join(media_dir, instance.image)
                if os.path.exists(old_path):
                    os.remove(old_path)
            instance.image = filename
            instance.save()

    def create(self, validated_data):
        titles_data = validated_data.pop('titles', None)
        lists_data = validated_data.pop('lists', None)
        validated_data.pop('image_file', None)

        instance = AppDownload.objects.create(**validated_data)
        self._save_image(instance, self.context.get('request'))

        if titles_data:
            for i, t in enumerate(titles_data):
                t['index'] = t.get('index', i + 1)
                AppDownloadTitle.objects.create(app_download=instance, **t)
        if lists_data:
            for i, l in enumerate(lists_data):
                l['index'] = l.get('index', i + 1)
                AppDownloadList.objects.create(app_download=instance, **l)

        return instance

    def update(self, instance, validated_data):
        titles_data = validated_data.pop('titles', None)
        lists_data = validated_data.pop('lists', None)
        validated_data.pop('image_file', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        self._save_image(instance, self.context.get('request'))

        if titles_data is not None:
            instance.titles.all().delete()
            for i, t in enumerate(titles_data):
                t['index'] = t.get('index', i + 1)
                AppDownloadTitle.objects.create(app_download=instance, **t)

        if lists_data is not None:
            instance.lists.all().delete()
            for i, l in enumerate(lists_data):
                l['index'] = l.get('index', i + 1)
                AppDownloadList.objects.create(app_download=instance, **l)

        return instance
