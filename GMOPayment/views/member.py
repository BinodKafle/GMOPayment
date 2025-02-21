import logging
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from GMOPayment.models.member import Member
from GMOPayment.serializers.member import MemberSerializer
from GMOPayment.services.member import GMOMemberService


class MemberViewSet(generics.CreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    service = GMOMemberService()

    def create(self, request, *args, **kwargs):
        try:
            member_id = request.data.get("member_id")
            if not member_id:
                raise ValidationError("Member ID is required.")
            response = self.service.create_member(member_id, request.data.get("name"))
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            logging.error(f"GMO Member creation failed: {str(e)}")
            raise ValidationError({"error": str(e)})


class MemberRetrieveView(APIView):
    service = GMOMemberService()

    def post(self, request, *args, **kwargs):
        member_id = request.data.get("member_id")
        if not member_id:
            raise ValidationError("Member ID is required.")
        response = self.service.get_member(member_id)
        return Response(response, status=status.HTTP_200_OK)
