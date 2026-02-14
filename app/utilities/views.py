from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from app.models.models import Document, Collateral, Conditions, Pages, Branches, BranchCategory, BranchPageSettings, HrPolicy, JobTranslations, Jobs, Footer, FloatMenu, FloatMenuSubmenus
from app.utilities.document.serializers.read import DocumentReadSerializer
from app.utilities.document.serializers.write import DocumentWriteSerializer
from app.utilities.collateral.serializers.read import CollateralReadSerializer
from app.utilities.collateral.serializers.write import CollateralWriteSerializer
from app.utilities.conditions.serializers.read import ConditionReadSerializer
from app.utilities.conditions.serializers.write import ConditionWriteSerializer
from app.utilities.pages.serializers.read import PagesReadSerializer
from app.utilities.pages.serializers.write import PagesWriteSerializer
from app.utilities.branch.serializers.read import BranchesReadSerializer, BranchCategorySerializer, BranchPageSettingsSerializer
from app.utilities.branch.serializers.write import BranchesWriteSerializer
from app.utilities.hrpolicy.serializers.read import  HrPolicyReadSerializer
from app.utilities.hrpolicy.serializers.write import HrPolicyWriteSerializer
from app.utilities.jobs.serializers.read import JobReadSerializer
from app.utilities.jobs.serializers.write import JobWriteSerializer
from app.utilities.footer.serializers.read import FooterReadSerializer 
from app.utilities.footer.serializers.write import FooterWriteSerializer
from app.utilities.floatMenu.serializers.serializers import ( FloatMenuReadSerializer,
    FloatMenuWriteSerializer,
    FloatMenuSubmenusReadSerializer,
    FloatMenuSubmenuCreateSerializer,
    FloatMenuSubmenuUpdateSerializer)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().prefetch_related(
        "documenttranslation_set",
        "documenttranslation_set__language"
    )

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return DocumentReadSerializer
        return DocumentWriteSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = DocumentWriteSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        
        read_serializer = DocumentReadSerializer(instance)
        headers = self.get_success_headers(read_serializer.data)
        
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        write_serializer = DocumentWriteSerializer(
            instance, 
            data=request.data, 
            partial=partial
        )
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        
        read_serializer = DocumentReadSerializer(instance)
        return Response(read_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        read_serializer = DocumentReadSerializer(instance)
        data = read_serializer.data
        
        instance.delete()
        
        return Response(
            {
                "message": "Document амжилттай устгагдлаа",
                "deleted_data": data
            },
            status=status.HTTP_200_OK
        )
    
class CollateralViewSet(viewsets.ModelViewSet):
    queryset = Collateral.objects.all().prefetch_related(
        "collateraltranslation_set",
        "collateraltranslation_set__language"
    )

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CollateralReadSerializer
        return CollateralWriteSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = CollateralWriteSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        
        read_serializer = CollateralReadSerializer(instance)
        headers = self.get_success_headers(read_serializer.data)
        
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        write_serializer = CollateralWriteSerializer(
            instance, 
            data=request.data, 
            partial=partial
        )
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        
        read_serializer = CollateralReadSerializer(instance)
        return Response(read_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        read_serializer = CollateralReadSerializer(instance)
        data = read_serializer.data
        
        instance.delete()
        
        return Response(
            {
                "message": "Collateral амжилттай устгагдлаа",
                "deleted_data": data
            },
            status=status.HTTP_200_OK
        )
    
class ConditionViewSet(viewsets.ModelViewSet):
    queryset = Conditions.objects.all().prefetch_related(
        "conditiontranslations_set",
        "conditiontranslations_set__language"
    )

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ConditionReadSerializer
        return ConditionWriteSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = ConditionWriteSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        
        read_serializer = ConditionReadSerializer(instance)
        headers = self.get_success_headers(read_serializer.data)
        
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        write_serializer = ConditionWriteSerializer(
            instance, 
            data=request.data, 
            partial=partial
        )
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        
        read_serializer = ConditionReadSerializer(instance)
        return Response(read_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        read_serializer = ConditionReadSerializer(instance)
        data = read_serializer.data
        
        instance.delete()
        
        return Response(
            {
                "message": "Condition амжилттай устгагдлаа",
                "deleted_data": data
            },
            status=status.HTTP_200_OK
        )
    

class PagesViewSet(viewsets.ModelViewSet):
    queryset = Pages.objects.all().prefetch_related(
        "pagetitletranslations_set",
        "pagetitletranslations_set__language",
        "pagedescriptiontranslations_set",
        "pagedescriptiontranslations_set__language"
    )

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PagesReadSerializer
        return PagesWriteSerializer

    @action(detail=False, methods=['get'], url_path='by-url')
    def by_url(self, request):
        """Lookup a page by its URL field, e.g. /api/v1/page/by-url/?url=/about-us"""
        page_url = request.query_params.get('url', '')
        if not page_url:
            return Response({'detail': 'url parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        # Try exact match first, then with/without leading slash
        page = Pages.objects.filter(url=page_url).first()
        if not page and not page_url.startswith('/'):
            page = Pages.objects.filter(url=f'/{page_url}').first()
        if not page and page_url.startswith('/'):
            page = Pages.objects.filter(url=page_url[1:]).first()
        if not page:
            return Response({'detail': 'Page not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PagesReadSerializer(page)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        write_serializer = PagesWriteSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        
        read_serializer = PagesReadSerializer(instance)
        headers = self.get_success_headers(read_serializer.data)
        
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        write_serializer = PagesWriteSerializer(
            instance, 
            data=request.data, 
            partial=partial
        )
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        
        read_serializer = PagesReadSerializer(instance)
        return Response(read_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        read_serializer = PagesReadSerializer(instance)
        data = read_serializer.data
        
        instance.delete()
        
        return Response(
            {
                "message": "Page амжилттай устгагдлаа",
                "deleted_data": data
            },
            status=status.HTTP_200_OK
        )
    

class BranchesViewSet(viewsets.ModelViewSet):
    queryset = Branches.objects.all().select_related("category").prefetch_related("branchphone_set")
    parser_classes = (MultiPartParser, FormParser)  

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return BranchesReadSerializer
        return BranchesWriteSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = BranchesWriteSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        
        read_serializer = BranchesReadSerializer(instance)
        headers = self.get_success_headers(read_serializer.data)
        
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        write_serializer = BranchesWriteSerializer(
            instance, 
            data=request.data, 
            partial=partial
        )
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        
        read_serializer = BranchesReadSerializer(instance)
        return Response(read_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        read_serializer = BranchesReadSerializer(instance)
        data = read_serializer.data
        
        if instance.image:
            clean_filename = instance.image.replace('media/', '').replace('branches/', '')
            image_path = os.path.join(settings.MEDIA_ROOT, 'branches', clean_filename)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Error deleting image: {e}")
        
        instance.delete()
        
        return Response(
            {
                "message": "Branch амжилттай устгагдлаа",
                "deleted_data": data
            },
            status=status.HTTP_200_OK
        )
    

class BranchCategoryViewSet(viewsets.ModelViewSet):
    queryset = BranchCategory.objects.all().order_by('sort_order', 'id')
    serializer_class = BranchCategorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Ангилал устгагдлаа"}, status=status.HTTP_200_OK)


class BranchPageSettingsViewSet(viewsets.ModelViewSet):
    queryset = BranchPageSettings.objects.all()
    serializer_class = BranchPageSettingsSerializer

    def list(self, request, *args, **kwargs):
        instance = BranchPageSettings.objects.first()
        if not instance:
            instance = BranchPageSettings.objects.create()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        instance = BranchPageSettings.objects.first()
        if not instance:
            instance = BranchPageSettings.objects.create()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class HrPolicyViewSet(viewsets.ModelViewSet):
    queryset = HrPolicy.objects.all().prefetch_related(
        'hrpolicytranslations_set',
        'hrpolicytranslations_set__language'
    ).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return HrPolicyReadSerializer
        return HrPolicyWriteSerializer
    
    def create(self, request, *args, **kwargs):
        write_serializer = HrPolicyWriteSerializer(
            data=request.data,
            context={'request': request}
        )
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        
        read_serializer = HrPolicyReadSerializer(
            instance,
            context={'request': request}
        )
        headers = self.get_success_headers(read_serializer.data)
        
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        write_serializer = HrPolicyWriteSerializer(
            instance,
            data=request.data,
            partial=partial,
            context={'request': request}
        )
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        
        read_serializer = HrPolicyReadSerializer(
            instance,
            context={'request': request}
        )
        return Response(read_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        read_serializer = HrPolicyReadSerializer(
            instance,
            context={'request': request}
        )
        data = read_serializer.data
        
        instance.delete()
        
        return Response(
            {
                "message": "HR Policy амжилттай устгагдлаа",
                "deleted_data": data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active policies"""
        active_policies = self.queryset.filter(active=True)
        serializer = HrPolicyReadSerializer(
            active_policies,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle active status"""
        instance = self.get_object()
        instance.active = not instance.active
        instance.save()
        
        serializer = HrPolicyReadSerializer(
            instance,
            context={'request': request}
        )
        return Response(serializer.data)
    

class JobViewSet(viewsets.ViewSet):

    
    def list(self, request):

        queryset = Jobs.objects.all().order_by('-date')
        serializer = JobReadSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
      
        serializer = JobWriteSerializer(data=request.data)
        
        if serializer.is_valid():
            job = serializer.save()
            read_serializer = JobReadSerializer(job)
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):

        job = get_object_or_404(Jobs, pk=pk)
        serializer = JobReadSerializer(job)
        return Response(serializer.data)
    
    def update(self, request, pk=None):

        job = get_object_or_404(Jobs, pk=pk)
        serializer = JobWriteSerializer(job, data=request.data)
        
        if serializer.is_valid():
            job = serializer.save()
            read_serializer = JobReadSerializer(job)
            return Response(read_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):

        job = get_object_or_404(Jobs, pk=pk)
        serializer = JobWriteSerializer(job, data=request.data, partial=True)
        
        if serializer.is_valid():
            job = serializer.save()
            read_serializer = JobReadSerializer(job)
            return Response(read_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):

        job = get_object_or_404(Jobs, pk=pk)
        job.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        queryset = Jobs.objects.filter(status=1).order_by('-date')
        serializer = JobReadSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
  
        job_type = request.query_params.get('type')
        if not job_type:
            return Response(
                {"error": "Алдаа гарлаа."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = Jobs.objects.filter(type=job_type).order_by('-date')
        serializer = JobReadSerializer(queryset, many=True)
        return Response(serializer.data)
    

class FooterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Footer with nested socials and urls + image upload
    
    GET /footer/ - List all footers
    GET /footer/{id}/ - Retrieve single footer
    POST /footer/ - Create new footer (multipart/form-data)
    PUT /footer/{id}/ - Update footer (multipart/form-data)
    PATCH /footer/{id}/ - Partial update footer
    DELETE /footer/{id}/ - Delete footer
    """
    queryset = Footer.objects.all().prefetch_related('footersocials_set', 'footerurls_set')
    parser_classes = (MultiPartParser, FormParser)
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FooterReadSerializer
        return FooterWriteSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = FooterReadSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = FooterReadSerializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        write_serializer = FooterWriteSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        footer = write_serializer.save()
        
        read_serializer = FooterReadSerializer(footer)
        headers = self.get_success_headers(read_serializer.data)
        
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        write_serializer = FooterWriteSerializer(
            instance,
            data=request.data,
            partial=partial
        )
        write_serializer.is_valid(raise_exception=True)
        footer = write_serializer.save()
        
        read_serializer = FooterReadSerializer(footer)
        return Response(read_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        read_serializer = FooterReadSerializer(instance)
        data = read_serializer.data
        
        if instance.logo:
            clean_filename = instance.logo.replace('media/', '').replace('footer/', '')
            image_path = os.path.join(settings.MEDIA_ROOT, 'footer', clean_filename)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"✅ Logo deleted: {clean_filename}")
                except Exception as e:
                    print(f"❌ Error deleting logo: {e}")
        
        instance.delete()
        
        return Response(
            {
                "message": "Footer амжилттай устгагдлаа",
                "deleted_data": data
            },
            status=status.HTTP_200_OK
        )
    

class FloatMenuViewSet(viewsets.ModelViewSet):
    queryset = FloatMenu.objects.all().prefetch_related(
        'floatmenutranslations_set',
        'floatmenusubmenus_set',
        'floatmenusubmenus_set__floatmenusubmenustranslations_set'
    )
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'get_submenus']:
            return FloatMenuReadSerializer
        return FloatMenuWriteSerializer
    
    def list(self, request, *args, **kwargs):
        """List all float menus with nested data"""
        queryset = self.get_queryset()
        serializer = FloatMenuReadSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve single float menu with nested data"""
        instance = self.get_object()
        serializer = FloatMenuReadSerializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Create new float menu with translations and submenus
        
        Expected JSON format for translations and submenus:
        {
            "iconcolor": "#000000",
            "fontfamily": "Arial",
            "bgcolor": "#ffffff",
            "fontcolor": "#000000",
            "image": <file>,
            "svg": "<svg>...</svg>",
            "translations": [
                {"language": 1, "label": "Main Menu"},
                {"language": 2, "label": "Үндсэн цэс"}
            ],
            "submenus": [
                {
                    "url": "/about",
                    "file": <file>,
                    "fontfamily": "Arial",
                    "bgcolor": "#f0f0f0",
                    "fontcolor": "#333333",
                    "translations": [
                        {"language": 1, "title": "About"},
                        {"language": 2, "title": "Тухай"}
                    ]
                }
            ]
        }
        """
        # Handle JSON strings for nested data
        data = request.data.copy()
        
        # Parse translations if it's a JSON string
        if 'translations' in data and isinstance(data['translations'], str):
            import json
            data['translations'] = json.loads(data['translations'])
        
        # Parse submenus if it's a JSON string
        if 'submenus' in data and isinstance(data['submenus'], str):
            import json
            data['submenus'] = json.loads(data['submenus'])
        
        write_serializer = FloatMenuWriteSerializer(data=data)
        write_serializer.is_valid(raise_exception=True)
        float_menu = write_serializer.save()
        
        read_serializer = FloatMenuReadSerializer(float_menu)
        headers = self.get_success_headers(read_serializer.data)
        
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def update(self, request, *args, **kwargs):
        """Update float menu with translations and submenus"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Handle JSON strings for nested data
        data = request.data.copy()
        
        # Parse translations if it's a JSON string
        if 'translations' in data and isinstance(data['translations'], str):
            import json
            data['translations'] = json.loads(data['translations'])
        
        # Parse submenus if it's a JSON string
        if 'submenus' in data and isinstance(data['submenus'], str):
            import json
            data['submenus'] = json.loads(data['submenus'])
        
        write_serializer = FloatMenuWriteSerializer(
            instance,
            data=data,
            partial=partial
        )
        write_serializer.is_valid(raise_exception=True)
        float_menu = write_serializer.save()
        
        read_serializer = FloatMenuReadSerializer(float_menu)
        return Response(read_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete float menu and all associated files"""
        instance = self.get_object()
        read_serializer = FloatMenuReadSerializer(instance)
        data = read_serializer.data
        
        # Delete main menu image if exists
        if instance.image:
            clean_filename = instance.image.replace('media/', '').replace('float_menu/', '')
            image_path = os.path.join(settings.MEDIA_ROOT, 'float_menu', clean_filename)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"✅ FloatMenu image deleted: {clean_filename}")
                except Exception as e:
                    print(f"❌ Error deleting FloatMenu image: {e}")
        
        # Delete all submenu files
        for submenu in instance.floatmenusubmenus_set.all():
            if submenu.file:
                clean_filename = submenu.file.replace('media/', '').replace('float_menu/', '').replace('submenus/', '')
                file_path = os.path.join(settings.MEDIA_ROOT, 'float_menu', 'submenus', clean_filename)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"✅ Submenu file deleted: {clean_filename}")
                    except Exception as e:
                        print(f"❌ Error deleting submenu file: {e}")
        
        instance.delete()
        
        return Response(
            {
                "message": "FloatMenu амжилттай устгагдлаа",
                "deleted_data": data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def submenus(self, request, pk=None):
        """
        Get all submenus for a specific float menu
        GET /float-menu/{id}/submenus/
        """
        float_menu = self.get_object()
        submenus = float_menu.floatmenusubmenus_set.all()
        serializer = FloatMenuSubmenusReadSerializer(submenus, many=True)
        return Response(serializer.data)


class FloatMenuSubmenuViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing FloatMenu submenus independently
    
    GET /float-menu-submenu/ - List all submenus
    GET /float-menu-submenu/{id}/ - Retrieve single submenu
    POST /float-menu-submenu/ - Create new submenu (multipart/form-data)
    PUT /float-menu-submenu/{id}/ - Update submenu (multipart/form-data)
    PATCH /float-menu-submenu/{id}/ - Partial update submenu
    DELETE /float-menu-submenu/{id}/ - Delete submenu
    """
    queryset = FloatMenuSubmenus.objects.all().prefetch_related(
        'floatmenusubmenustranslations_set'
    )
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FloatMenuSubmenusReadSerializer
        elif self.action == 'create':
            return FloatMenuSubmenuCreateSerializer
        else:
            return FloatMenuSubmenuUpdateSerializer
    
    def list(self, request, *args, **kwargs):
        """
        List all submenus with optional filtering by float_menu
        Query params:
        - float_menu: Filter by float menu ID
        """
        queryset = self.get_queryset()
        
        # Filter by float_menu if provided
        float_menu_id = request.query_params.get('float_menu', None)
        if float_menu_id is not None:
            queryset = queryset.filter(float_menu_id=float_menu_id)
        
        serializer = FloatMenuSubmenusReadSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve single submenu with translations"""
        instance = self.get_object()
        serializer = FloatMenuSubmenusReadSerializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Create new submenu
        
        Expected format:
        {
            "float_menu": 1,
            "url": "/contact",
            "file": <file>,
            "fontfamily": "Arial",
            "bgcolor": "#f5f5f5",
            "fontcolor": "#333333",
            "translations": [
                {"language": 1, "title": "Contact"},
                {"language": 2, "title": "Холбоо барих"}
            ]
        }
        """
        # Handle JSON strings for nested data
        data = request.data.copy()
        
        # Parse translations if it's a JSON string
        if 'translations' in data and isinstance(data['translations'], str):
            import json
            data['translations'] = json.loads(data['translations'])
        
        write_serializer = FloatMenuSubmenuCreateSerializer(data=data)
        write_serializer.is_valid(raise_exception=True)
        submenu = write_serializer.save()
        
        read_serializer = FloatMenuSubmenusReadSerializer(submenu)
        headers = self.get_success_headers(read_serializer.data)
        
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def update(self, request, *args, **kwargs):
        """Update submenu"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Handle JSON strings for nested data
        data = request.data.copy()
        
        # Parse translations if it's a JSON string
        if 'translations' in data and isinstance(data['translations'], str):
            import json
            data['translations'] = json.loads(data['translations'])
        
        write_serializer = FloatMenuSubmenuUpdateSerializer(
            instance,
            data=data,
            partial=partial
        )
        write_serializer.is_valid(raise_exception=True)
        submenu = write_serializer.save()
        
        read_serializer = FloatMenuSubmenusReadSerializer(submenu)
        return Response(read_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete submenu and associated file"""
        instance = self.get_object()
        read_serializer = FloatMenuSubmenusReadSerializer(instance)
        data = read_serializer.data
        
        # Delete submenu file if exists
        if instance.file:
            clean_filename = instance.file.replace('media/', '').replace('float_menu/', '').replace('submenus/', '')
            file_path = os.path.join(settings.MEDIA_ROOT, 'float_menu', 'submenus', clean_filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"✅ Submenu file deleted: {clean_filename}")
                except Exception as e:
                    print(f"❌ Error deleting submenu file: {e}")
        
        instance.delete()
        
        return Response(
            {
                "message": "FloatMenu submenu амжилттай устгагдлаа",
                "deleted_data": data
            },
            status=status.HTTP_200_OK
        )