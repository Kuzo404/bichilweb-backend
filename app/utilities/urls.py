from rest_framework.routers import DefaultRouter
from app.utilities.views import CollateralViewSet, ConditionViewSet, DocumentViewSet, PagesViewSet, BranchesViewSet, BranchCategoryViewSet, BranchPageSettingsViewSet, HrPolicyViewSet, JobViewSet, FooterViewSet, FloatMenuViewSet, FloatMenuSubmenuViewSet, FloatMenuSocialsViewSet

router = DefaultRouter()

router.register(r"document", DocumentViewSet, basename="document")
router.register(r"collateral", CollateralViewSet, basename="collateral")
router.register(r"condition", ConditionViewSet, basename="condition")
router.register(r"page", PagesViewSet, basename="page")
router.register(r"branch", BranchesViewSet, basename="branch")
router.register(r"branch-category", BranchCategoryViewSet, basename="branch-category")
router.register(r"branch-settings", BranchPageSettingsViewSet, basename="branch-settings")
router.register(r"hrpolicy", HrPolicyViewSet, basename="hrpolicy")
router.register(r"jobs", JobViewSet, basename="jobs")
router.register(r"footer", FooterViewSet, basename="footer")
router.register(r"float-menu", FloatMenuViewSet, basename="floatmenu")
router.register(r"float-submenu", FloatMenuSubmenuViewSet, basename="floatsubmenu")
router.register(r"float-menu-socials", FloatMenuSocialsViewSet, basename="floatmenusocials")

urlpatterns = router.urls
