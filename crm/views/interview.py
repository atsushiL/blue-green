from rest_framework.permissions import IsAuthenticated
from crm.permission import IsGeneralUser, IsSuperUser
from django.forms import model_to_dict
from rest_framework.viewsets import ModelViewSet
from crm.models import Interview, InterviewHistory
from crm.serializers.interview import InterviewSerializer


class InterviewViewSet(ModelViewSet):
    serializer_class = InterviewSerializer

    def get_queryset(self):
        return Interview.objects.filter(
            provisional_customer_id=self.kwargs["provisional_customer_pk"]
        )

    def perform_create(self, serializer):
        serializer.save(
            provisional_customer_id=self.kwargs["provisional_customer_pk"],
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        interview = self.get_object()
        data = model_to_dict(interview)
        data["interview_id"] = interview.id
        data["created_at"] = interview.created_at
        data["interview_item_id"] = data.pop("interview_item")
        data["provisional_customer_id"] = data.pop("provisional_customer")
        data["created_by_id"] = data.pop("created_by")

        InterviewHistory.objects.create(**data)

        serializer.save(
            provisional_customer_id=self.kwargs["provisional_customer_pk"],
            created_by=self.request.user,
        )
        customer = interview.provisional_customer.customer
        customer.updated_by = self.request.user
        customer.save()

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]
