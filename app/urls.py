from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.views.headers import HeaderViewSet  
from app.views.headersMenu import HeaderMenuViewSet
from app.views.headersSubmenu import HeaderSubmenuViewSet
from app.views.headersTertiaryMenu import HeaderTertiaryMenuViewSet
from app.views.headerStyle import HeaderStyleViewSet
from app.views.heroSlider import HeroSliderViewSet
from app.views.cta import CtaViewSet
from app.views.appDownload import AppDownloadViewSet
from app.views.upload import FileUploadView

router = DefaultRouter()
router.register(r'headers', HeaderViewSet, basename='header')
router.register(r'header-menu', HeaderMenuViewSet, basename='header-menu')
router.register(r'header-submenu', HeaderSubmenuViewSet, basename='header-submenu')
router.register(r'header-tertiary', HeaderTertiaryMenuViewSet, basename='header-tertiary')
router.register(r'header-style', HeaderStyleViewSet, basename='header-style')
router.register(r'hero-slider', HeroSliderViewSet, basename='hero-slider')
router.register(r'CTA', CtaViewSet, basename='CTA')
router.register(r'app-download', AppDownloadViewSet, basename='app-download')

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
]
