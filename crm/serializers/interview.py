from rest_framework import serializers
from crm.models import Interview


class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = "__all__"
        read_only_fields = ["id", "created_at", "provisional_customer", "created_by"]

    def to_representation(self, instance):
        rep = super(InterviewSerializer, self).to_representation(instance)
        rep["interview_item_name"] = instance.interview_item.item
        return rep
