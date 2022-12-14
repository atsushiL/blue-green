import django_filters
from django.db.models import Max, Q, Subquery, OuterRef
from crm.models import (
    EvaluateCompany,
    IntroductionCompany,
    ProspectCustomer,
    ProspectCustomerData,
    ProvisionalCustomer,
    ProvisionalCustomerData,
    User,
    CustomerData,
    Customer,
    CustomerNegotiationHistory,
)

def get_newest_customer_data(queryset, customer_status, query):
    new_queryset = queryset.filter(
        customer_id__in=CustomerData.objects.filter(
            created_at=Subquery(
                (CustomerData.objects.filter(Q(customer_id=OuterRef('customer_id'))&Q(customer__customer_status=customer_status))
                .values('customer_id')
                .annotate(last_date=Max("created_at"))
                .values('last_date')[:1]
                )
            )    
        ).filter(query).values_list("customer_id", flat=True)
    )
    
    return new_queryset


def get_newest_provisional_customer_data(queryset, query, estate=False):
    data_query = ProvisionalCustomerData.objects.filter(
        created_at=Subquery(
            (ProvisionalCustomerData.objects
            .filter(Q(provisional_customer_id=OuterRef('provisional_customer_id')) & Q(provisional_customer__customer__customer_status=Customer.CustomerStatus.PROVISIONAL))
            .values('provisional_customer_id')
            .annotate(last_date=Max("created_at"))
            .values('last_date')[:1]
            )
        )    
    )

    if estate:
        new_queryset = queryset.filter(customer__provisional_customer__id__in=data_query.filter(query).values_list("provisional_customer_id", flat=True))
    else:
        new_queryset = queryset.filter(pk__in=data_query.filter(query).values_list("provisional_customer_id", flat=True))
    
    return new_queryset


def get_newest_prospect_customer_data(queryset, query):
    new_queryset = queryset.filter(
        pk__in=ProspectCustomerData.objects.filter(
            created_at=Subquery(
                (ProspectCustomerData.objects
                .filter(Q(prospect_customer_id=OuterRef('prospect_customer_id'))&Q(prospect_customer__customer__customer_status=Customer.CustomerStatus.PROSPECT))
                .values('prospect_customer_id')
                .annotate(last_date=Max("created_at"))
                .values('last_date')[:1]
                )
            )
        ).filter(query).values_list("prospect_customer_id", flat=True)
    )
    
    return new_queryset


def get_newest_customer_negotiation(queryset, status, query):
    new_queryset = queryset.filter(
        customer_id__in=CustomerNegotiationHistory.objects.filter(
                negotiation_datetime=Subquery(
                    (CustomerNegotiationHistory.objects
                    .filter(Q(customer_id=OuterRef('customer_id'))&Q(customer__customer_status=status))
                    .values('customer_id')
                    .annotate(last_date=Max("negotiation_datetime"))
                    .values('last_date')[:1]
                    )
                )
        ).filter(query).values_list("customer_id", flat=True)
    )
    
    return new_queryset


# ?????????????????????????????????????????????
class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="contains")
    username = django_filters.CharFilter(field_name="username", lookup_expr="contains")

    class Meta:
        model = User
        fields = ["name", "username"]


# ?????????????????????????????????(???????????????)????????????????????????????????????
class IntroductionCompanyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="contains")
    phone_no = django_filters.CharFilter(field_name="phone_no", lookup_expr="contains")
    person_in_charge = django_filters.CharFilter(
        field_name="person_in_charge", lookup_expr="contains"
    )

    class Meta:
        model = IntroductionCompany
        fields = ["name", "phone_no", "created_by"]


# ?????????????????????????????????????????????????????????????????????????????????????????????
class ProspectCustomerFilter(django_filters.FilterSet):
    prefecture = django_filters.CharFilter(method='get_by_prefecture', field_name='prospect_customer_data__prefecture')
    # ?????????
    created_at = django_filters.DateFromToRangeFilter(field_name="customer__created_at")
    # ???????????????
    negotiation_date = django_filters.DateFromToRangeFilter(method="get_by_customer_negotiation_date", field_name="customer__negotiation_history__negotiation_datetime")

    # ?????????????????????????????????????????????????????????
    name = django_filters.CharFilter(method="search_name", label="name")

    class Meta:
        model = ProspectCustomer
        fields = ["created_at"]

    def get_by_customer_negotiation_date(self, queryset, name, value):
        data = get_newest_customer_negotiation(queryset, Customer.CustomerStatus.PROSPECT, Q(negotiation_datetime__date__range=[self.data["negotiation_date_after"],self.data["negotiation_date_before"]]))
        return data

    def get_by_prefecture(self, queryset, name, value):
        data = get_newest_prospect_customer_data(queryset, Q(prefecture=self.data['prefecture']))
        return data

    def search_name(self, queryset, name, value):
        data = get_newest_customer_data(queryset, Customer.CustomerStatus.PROSPECT, (Q(name__contains=self.data["name"]) | Q(kana__contains=self.data["name"])))
        return data


# ???????????????????????????????????????????????????????????????????????????????????????????????????
class ProvisionalCustomerFilter(django_filters.FilterSet):
    approval = django_filters.BooleanFilter(
        field_name="provisional_customer_data__approval", method="get_by_approval"
    )
    # ????????????
    application_date = django_filters.DateFromToRangeFilter(
        field_name="provisional_customer_data__application_date", method="get_by_application_date"
    )
    # ???????????????
    negotiation_date = django_filters.DateFromToRangeFilter(method="get_by_customer_negotiation_date", field_name="customer__negotiation_history__negotiation_datetime")
    # ?????????????????????????????????????????????????????????
    name = django_filters.CharFilter(method="search_name", label="name")

    class Meta:
        model = ProvisionalCustomer
        fields = ["approval", "application_date"]

    def get_by_customer_negotiation_date(self, queryset, name, value):
        data = get_newest_customer_negotiation(queryset, Customer.CustomerStatus.PROVISIONAL, Q(negotiation_datetime__date__range=[self.data["negotiation_date_after"],self.data["negotiation_date_before"]]))
        return data
    
    def get_by_approval(self, queryset, name, value):
        data = get_newest_provisional_customer_data(queryset, Q(approval=self.data["approval"]))
        return data

    def get_by_application_date(self, queryset, name, value):
        data = get_newest_provisional_customer_data(queryset, Q(application_date__range=[self.data["application_date_after"],self.data["application_date_before"]]))
        return data

    def search_name(self, queryset, name, value):
        data = get_newest_customer_data(queryset, Customer.CustomerStatus.PROVISIONAL, (Q(name__contains=self.data["name"]) | Q(kana__contains=self.data["name"])))
        return data

class EstateFilter(django_filters.FilterSet):
    application_date = django_filters.DateFromToRangeFilter(method="get_by_application_date", label="application_date")
    name = django_filters.CharFilter(method="search_name", label="name")
    purchase_survey_result = django_filters.BooleanFilter(field_name="purchase_survey__result")

    def search_name(self, queryset, name, value):
        data = get_newest_customer_data(queryset, Customer.CustomerStatus.PROVISIONAL, (Q(name__contains=self.data["name"]) | Q(kana__contains=self.data["name"])))
        return data

    def get_by_application_date(self, queryset, name, value):
        data = get_newest_provisional_customer_data(queryset, Q(application_date__range=[self.data["application_date_after"],self.data["application_date_before"]]),estate=True)
        return data

class EvaluateCompanyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="contains")
    person_in_charge = django_filters.CharFilter(field_name="person_in_charge", lookup_expr="contains")
    created_at = django_filters.DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = EvaluateCompany
        fields = ["name", "person_in_charge", "created_at"]
