from django.urls import path, include
from rest_framework_nested import routers
from crm.views.estate_certificate import EstateCertificateViewSet
from crm.views.land_certificate import LandCertificateViewSet
from crm.views.login import LoginViewSet
from crm.views.user import UserViewSet
from crm.views.evaluation_standard import EvaluationStandardViewSet
from crm.views.interview_item import InterviewItemViewSet
from crm.views.promotion_result import PromotionResultViewSet
from crm.views.promotion_method import PromotionMethodViewSet
from crm.views.evaluate_company import EvaluateCompanyViewSet
from crm.views.introduction_company import IntroductionCompanyViewSet
from crm.views.prospect_customer import ProspectCustomerViewSet
from crm.views.estate import EstateViewSet
from crm.views.evaluate_company_evaluation import EvaluateCompanyEvaluationsViewSet
from crm.views.evaluation_result import EvaluationResultViewSet
from crm.views.provisional_customer import ProvisionalCustomerViewSet
from crm.views.workplace_info import WorkplaceInfoViewSet
from crm.views.customer import CustomerViewSet
from crm.views.bank_account import BankAccountViewSet
from crm.views.health_check import health_check
from crm.views.loan import LoanViewSet
from crm.views.alb_anti_social_check import ALB_Anti_Social_CheckViewSet
from crm.views.application_info import ApplicationInfoViewSet
from crm.views.customer_negotiation_history import CustomerNegotiationHistoryViewSet
from crm.views.anti_social_check_result import AntiSocialCheckResultViewSet
from crm.views.family import FamilyViewSet
from crm.views.land import LandViewSet
from crm.views.earnings_sim import EarningsSimViewSet
from crm.views.kouku import KoukuViewSet
from crm.views.otsuku import OtsukuViewSet
from crm.views.purchase_survey import PurchaseSurveyViewSet
from crm.views.interview import InterviewViewSet
from crm.views.building import BuildingViewSet

router = routers.DefaultRouter()
router.register(r"user", UserViewSet, basename="user")
router.register(r"", LoginViewSet, basename="login")
router.register(
    r"evaluation_standard", EvaluationStandardViewSet, basename="evaluation_standard"
)
router.register(r"interview_item", InterviewItemViewSet, basename="interview_item")
router.register(
    r"promotion_method", PromotionMethodViewSet, basename="promotion_method"
)

router.register(r"estates", EstateViewSet, basename="estate")
estate_router = routers.NestedSimpleRouter(router, r"estates", lookup="estate")
estate_router.register(r"building", BuildingViewSet, basename="building")
estate_router.register(r"land", LandViewSet, basename="land")
estate_router.register(
    r"evaluate_company_evaluation",
    EvaluateCompanyEvaluationsViewSet,
    basename="evaluate_company_evaluation",
)
estate_router.register(r"land_kouku", KoukuViewSet, basename="land_kouku")
estate_router.register(r"estate_kouku", KoukuViewSet, basename="estate_kouku")
estate_router.register(r"estate_otsuku", OtsukuViewSet, basename="estate_otsuku")
estate_router.register(r"land_otsuku", OtsukuViewSet, basename="land_otsuku")
estate_router.register(r"earnings_sim", EarningsSimViewSet, basename="earnings_sim")
estate_router.register(
    r"purchase_survey", PurchaseSurveyViewSet, basename="purchase_survey"
)
estate_router.register(
    r"estate_certificate", EstateCertificateViewSet, basename="estate_certificate"
)
estate_router.register(
    r"evaluation_result", EvaluationResultViewSet, basename="evaluation_result"
)
estate_router.register(
    r"land_certificate", LandCertificateViewSet, basename="land_certificate"
)
router.register(
    r"prospect_customers", ProspectCustomerViewSet, basename="prospect_customers"
)
router.register(
    r"promotion_result", PromotionResultViewSet, basename="promotion_result"
)
router.register(
    r"evaluate_company", EvaluateCompanyViewSet, basename="evaluate_company"
)
router.register(
    r"introduction_company", IntroductionCompanyViewSet, basename="introduction_company"
)
router.register(
    r"alb_anti_social_check",
    ALB_Anti_Social_CheckViewSet,
    basename="alb_anti_social_check",
)

router.register(r"customers", CustomerViewSet, basename="customer")

prospect_customer = routers.NestedSimpleRouter(router, r"prospect_customers", lookup="prospect_customer")
prospect_customer.register(
    r"customer_negotiation_history",
    CustomerNegotiationHistoryViewSet,
    basename="customer_negotiation_history",
)

router.register(
    r"provisional_customers",
    ProvisionalCustomerViewSet,
    basename="provisional_customer",
)
provisional_customers_router = routers.NestedSimpleRouter(
    router, r"provisional_customers", lookup="provisional_customer"
)
provisional_customers_router.register(r"workplace", WorkplaceInfoViewSet, basename="workplace")
provisional_customers_router.register(r"bank_account", BankAccountViewSet, basename="bank_account")
provisional_customers_router.register(r"loan", LoanViewSet, basename="loan")
provisional_customers_router.register(
    r"application_info", ApplicationInfoViewSet, basename="application_info"
)
provisional_customers_router.register(
    r"anti_check", AntiSocialCheckResultViewSet, basename="anti_check"
)
provisional_customers_router.register(r"family", FamilyViewSet, basename="family")
provisional_customers_router.register(
    r"interview", InterviewViewSet, basename="interview")
provisional_customers_router.register(
    r"customer_negotiation_history",
    CustomerNegotiationHistoryViewSet,
    basename="customer_negotiation_history",
)
urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(prospect_customer.urls)),
    path(r"", include(estate_router.urls)),
    path(r"", include(provisional_customers_router.urls)),
    path(r"health/", health_check, name="health"),
]
