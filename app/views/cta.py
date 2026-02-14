# =============================================================================
# VIEWSET - Updated to handle Language object
# =============================================================================
# app/views/cta.py

from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
import os
import json
import time

from app.models.models import Cta, CtaTitle, CtaSubtitle
from app.serializers.cta import CtaSerializer


class CtaViewSet(ModelViewSet):
    queryset = Cta.objects.all().order_by('index')
    serializer_class = CtaSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):
        """Create new CTA slide"""
        try:
            data = {}
            data['number'] = request.data.get('number')
            data['index'] = request.data.get('index')
            data['font'] = request.data.get('font')
            data['color'] = request.data.get('color')
            data['description'] = request.data.get('description', '')
            data['url'] = request.data.get('url', '')
            if 'file' in request.FILES:
                file = request.FILES['file']
                save_path = self._save_file(file)
                data['file'] = save_path
            else:
                return Response(
                    {'error': 'File is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cta үүсгэх
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            cta_instance = serializer.save()
            
            # Titles үүсгэх
            titles_json = request.data.get('titles')
            if titles_json:
                try:
                    titles_data = json.loads(titles_json) if isinstance(titles_json, str) else titles_json
                    for title_item in titles_data:
                        language_value = title_item.get('language')
                        
                        # ✅ Language model шалгах
                        if self._has_language_model():
                            from app.models.models import Language
                            language_obj = Language.objects.get(id=language_value)
                            CtaTitle.objects.create(
                                cta=cta_instance,
                                language=language_obj,
                                label=title_item.get('label', '')
                            )
                        else:
                            # IntegerField бол шууд хадгална
                            CtaTitle.objects.create(
                                cta=cta_instance,
                                language=language_value,
                                label=title_item.get('label', '')
                            )
                except json.JSONDecodeError as e:
                    print(f"Titles JSON parse error: {e}")
                except Exception as e:
                    print(f"Titles create error: {e}")
            
            # Subtitles үүсгэх
            subtitles_json = request.data.get('subtitles')
            if subtitles_json:
                try:
                    subtitles_data = json.loads(subtitles_json) if isinstance(subtitles_json, str) else subtitles_json
                    for subtitle_item in subtitles_data:
                        language_value = subtitle_item.get('language')
                        
                        # ✅ Language model шалгах
                        if self._has_language_model():
                            from app.models.models import Language
                            language_obj = Language.objects.get(id=language_value)
                            CtaSubtitle.objects.create(
                                cta=cta_instance,
                                language=language_obj,
                                label=subtitle_item.get('label', '')
                            )
                        else:
                            # IntegerField бол шууд хадгална
                            CtaSubtitle.objects.create(
                                cta=cta_instance,
                                language=language_value,
                                label=subtitle_item.get('label', '')
                            )
                except json.JSONDecodeError as e:
                    print(f"Subtitles JSON parse error: {e}")
                except Exception as e:
                    print(f"Subtitles create error: {e}")
            
            # Response буцаах
            response_serializer = self.get_serializer(cta_instance)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            print(f"Create error: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """Update CTA slide"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            data = {}
            data['number'] = request.data.get('number', instance.number)
            data['index'] = request.data.get('index', instance.index)
            data['font'] = request.data.get('font', instance.font)
            data['color'] = request.data.get('color', instance.color)
            data['description'] = request.data.get('description', instance.description or '')
            data['url'] = request.data.get('url', instance.url or '')
            
            # Шинэ файл байвал
            if 'file' in request.FILES:
                file = request.FILES['file']
                
                # Хуучин файлыг устгах
                if instance.file and os.path.exists(instance.file):
                    os.remove(instance.file)
                
                save_path = self._save_file(file)
                data['file'] = save_path
            else:
                data['file'] = instance.file
            
            # Update хийх
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            cta_instance = serializer.save()
            
            # Titles шинэчлэх
            titles_json = request.data.get('titles')
            if titles_json:
                try:
                    instance.ctatitle_set.all().delete()
                    
                    titles_data = json.loads(titles_json) if isinstance(titles_json, str) else titles_json
                    for title_item in titles_data:
                        language_value = title_item.get('language')
                        
                        if self._has_language_model():
                            from app.models.models import Language
                            language_obj = Language.objects.get(id=language_value)
                            CtaTitle.objects.create(
                                cta=cta_instance,
                                language=language_obj,
                                label=title_item.get('label', '')
                            )
                        else:
                            CtaTitle.objects.create(
                                cta=cta_instance,
                                language=language_value,
                                label=title_item.get('label', '')
                            )
                except Exception as e:
                    print(f"Titles update error: {e}")
            
            # Subtitles шинэчлэх
            subtitles_json = request.data.get('subtitles')
            if subtitles_json:
                try:
                    instance.ctasubtitle_set.all().delete()
                    
                    subtitles_data = json.loads(subtitles_json) if isinstance(subtitles_json, str) else subtitles_json
                    for subtitle_item in subtitles_data:
                        language_value = subtitle_item.get('language')
                        
                        if self._has_language_model():
                            from app.models.models import Language
                            language_obj = Language.objects.get(id=language_value)
                            CtaSubtitle.objects.create(
                                cta=cta_instance,
                                language=language_obj,
                                label=subtitle_item.get('label', '')
                            )
                        else:
                            CtaSubtitle.objects.create(
                                cta=cta_instance,
                                language=language_value,
                                label=subtitle_item.get('label', '')
                            )
                except Exception as e:
                    print(f"Subtitles update error: {e}")
            
            response_serializer = self.get_serializer(cta_instance)
            return Response(response_serializer.data)
            
        except Exception as e:
            print(f"Update error: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """Delete CTA slide"""
        try:
            instance = self.get_object()
            
            # Файл устгах
            if instance.file and os.path.exists(instance.file):
                os.remove(instance.file)
            
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _save_file(self, file):
        """Save uploaded file and return path"""
        save_folder = 'media/cta_files'
        os.makedirs(save_folder, exist_ok=True)
        
        timestamp = str(int(time.time() * 1000))
        ext = os.path.splitext(file.name)[1]
        filename = f"cta_{timestamp}{ext}"
        
        save_path = os.path.join(save_folder, filename)
        
        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        return save_path.replace('\\', '/')
    
    def _has_language_model(self):
        """Check if Language model exists"""
        try:
            from app.models.models import Language
            return True
        except ImportError:
            return False


# =============================================================================
# QUICK FIX - If you just want to make it work NOW
# =============================================================================
"""
Just update your serializer's get_titles and get_subtitles methods:

def get_titles(self, obj):
    titles = []
    for t in obj.ctatitle_set.all():
        # Convert Language object to ID
        lang_id = t.language.id if hasattr(t.language, 'id') else t.language
        titles.append({
            "id": t.id,
            "language": lang_id,
            "label": t.label
        })
    return titles

def get_subtitles(self, obj):
    subtitles = []
    for s in obj.ctasubtitle_set.all():
        # Convert Language object to ID
        lang_id = s.language.id if hasattr(s.language, 'id') else s.language
        subtitles.append({
            "id": s.id,
            "language": lang_id,
            "label": s.label
        })
    return subtitles
"""