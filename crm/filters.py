import django_filters
from django.db.models import Max, Q, Subquery, OuterRef
from crm.models import (
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
        customer_id__in=Subquery(
            CustomerData.objects.filter(
                created_at=Subquery(
                    (CustomerData.objects.filter(Q(customer_id=OuterRef('customer_id'))&Q(customer__customer_status=customer_status))
                    .values('customer_id')
                    .annotate(last_date=Max("created_at"))
                    .values('last_date')[:1]
                    )
                )    
            ).filter(query).values_list("customer_id", flat=True)
        )
    )
    
    return new_queryset

def get_newest_provisional_customer_data(queryset, query):
    new_queryset = queryset.filter(
        customer_id__in=Subquery(
            ProvisionalCustomerData.objects.filter(
                created_at=Subquery(
                    (ProvisionalCustomerData.objects
                    .filter(Q(provisional_customer_id=OuterRef('provisional_customer_id')) & Q(provisional_customer__customer__customer_status=Customer.CustomerStatus.PROVISIONAL))
                    .values('provisional_customer_id')
                    .annotate(last_date=Max("created_at"))
                    .values('last_date')[:1]
                    )
                )    
            ).filter(query).values_list("provisional_customer_id", flat=True)
        )
    )
    
    
    return new_queryset

def get_newest_prospect_customer_data(queryset, query):
    new_queryset = queryset.filter(
        customer_id__in=Subquery(
            ProspectCustomerData.objects.filter(
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
    )
    
    return new_queryset

def get_newest_customer_negotiation(queryset, status, query):
    new_queryset = queryset.filter(
        customer_id__in=Subquery(
            CustomerNegotiationHistory.objects.filter(
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
    )
    
    return new_queryset


# 社員番号、名前を検索・絞り込み
class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="contains")
    username = django_filters.CharFilter(field_name="username")

    class Meta:
        model = User
        fields = ["name", "username"]


# 紹介会社名、電話番号、(紹介会社の)担当者名を検索・絞り込み
class IntroductionCompanyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="contains")
    phone_no = django_filters.CharFilter(field_name="phone_no", lookup_expr="contains")
    person_in_charge = django_filters.CharFilter(
        field_name="person_in_charge", lookup_expr="contains"
    )

    class Meta:
        model = IntroductionCompany
        fields = ["name", "phone_no", "created_by"]


# お客様氏名（カナ含む）、都道府県、登録日、最終更新日を絞り込み
class ProspectCustomerFilter(django_filters.FilterSet):
    prefecture = django_filters.CharFilter(method='get_by_prefecture', field_name='prospect_customer_data__prefecture')
    # 登録日
    created_at = django_filters.DateFromToRangeFilter(field_name="customer__created_at")
    # 最終交渉日
    negotiation_date = django_filters.DateFromToRangeFilter(method="get_by_customer_negotiation_date", field_name="customer__negotiation_history__negotiation_datetime")

    # 漢字氏名とカナ氏名のどちらかで絞り込み
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


# 仮申込客様氏名（カナ含む）、都道府県、登録日、最終更新日を絞り込み
class ProvisionalCustomerFilter(django_filters.FilterSet):
    approval = django_filters.BooleanFilter(
        field_name="provisional_customer_data__approval", method="get_by_approval"
    )
    # 申込み日
    application_date = django_filters.DateFromToRangeFilter(
        field_name="provisional_customer_data__application_date", method="get_by_application_date"
    )
    # 最終交渉日
    negotiation_date = django_filters.DateFromToRangeFilter(method="get_by_customer_negotiation_date", field_name="customer__negotiation_history__negotiation_datetime")
    # 漢字氏名とカナ氏名のどちらかで絞り込み
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
