from rest_framework import serializers
from app.models.models import Branches, BranchPhone, BranchCategory
import json
import os
from django.conf import settings
import uuid


class BranchesWriteSerializer(serializers.ModelSerializer):
    phones = serializers.CharField(write_only=True)
    image = serializers.ImageField(required=False, allow_null=True, write_only=True)
    category_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    
    class Meta:
        model = Branches
        fields = [
            "id", "name", "location", "image", "area", "city", 
            "district", "open", "time", "latitude", "longitude", "phones",
            "category_id"
        ]
    
    def validate_phones(self, value):
        try:
            phones_data = json.loads(value) if isinstance(value, str) else value
            
            if not isinstance(phones_data, list):
                raise serializers.ValidationError("Утасны дугаар оруулна уу.")
            
            if not phones_data:
                raise serializers.ValidationError("Дор хаяж нэг утас оруулна уу")
            
            for phone in phones_data:
                if not isinstance(phone, dict) or 'phone' not in phone:
                    raise serializers.ValidationError("")
                if not phone['phone'].strip():
                    raise serializers.ValidationError("Утас хоосон байж болохгүй")
            
            return phones_data
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for phones")
    
    def _save_image(self, image_file):
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'branches')
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
            clean_filename = filename.replace('media/', '').replace('branches/', '')
            image_path = os.path.join(settings.MEDIA_ROOT, 'branches', clean_filename)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"✅ Image deleted: {clean_filename}")
                except Exception as e:
                    print(f"❌ Error deleting image: {e}")
    
    def create(self, validated_data):
        phones_data = validated_data.pop('phones')
        image_file = validated_data.pop('image', None)
        category_id = validated_data.pop('category_id', None)
        
        if image_file:
            filename = self._save_image(image_file)
            validated_data['image'] = filename
            print(f"✅ Image saved: {filename}")
        
        if category_id:
            try:
                cat = BranchCategory.objects.get(id=category_id)
                validated_data['category'] = cat
            except BranchCategory.DoesNotExist:
                pass
        
        branch = Branches.objects.create(**validated_data)
        
        for phone_data in phones_data:
            BranchPhone.objects.create(branch=branch, phone=phone_data['phone'])
        
        return branch
    
    def update(self, instance, validated_data):
        phones_data = validated_data.pop('phones', None)
        image_file = validated_data.pop('image', None)
        category_id = validated_data.pop('category_id', None)
        
        if image_file:
            if instance.image:
                self._delete_image(instance.image)
            filename = self._save_image(image_file)
            validated_data['image'] = filename
            print(f"✅ Image updated: {filename}")
        
        instance.name = validated_data.get('name', instance.name)
        instance.location = validated_data.get('location', instance.location)
        instance.area = validated_data.get('area', instance.area)
        instance.city = validated_data.get('city', instance.city)
        instance.district = validated_data.get('district', instance.district)
        instance.open = validated_data.get('open', instance.open)
        instance.time = validated_data.get('time', instance.time)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        
        if 'image' in validated_data:
            instance.image = validated_data['image']
        
        # Handle category
        if category_id is not None:
            if category_id == 0 or category_id == '':
                instance.category = None
            else:
                try:
                    instance.category = BranchCategory.objects.get(id=category_id)
                except BranchCategory.DoesNotExist:
                    pass
        
        instance.save()
        
        if phones_data is not None:
            instance.branchphone_set.all().delete()
            for phone_data in phones_data:
                BranchPhone.objects.create(branch=instance, phone=phone_data['phone'])
        
        return instance