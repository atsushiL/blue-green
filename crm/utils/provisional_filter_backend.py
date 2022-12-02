from django_filters.rest_framework import DjangoFilterBackend
from crm.filters import ProvisionalCustomerFilter


class ProvisionalFilterBackend(DjangoFilterBackend):
    def get_filterset(self, request, queryset, view):
        kwargs = self.get_filterset_kwargs(request, queryset, view)
        if view.action == "list":
            return ProvisionalCustomerFilter(**kwargs)
        return None
