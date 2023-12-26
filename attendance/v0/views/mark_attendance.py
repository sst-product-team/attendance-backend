from rest_framework import status, views
from rest_framework.response import Response
from rest_framework import exceptions

from rest_framework import serializers
from django.utils.functional import cached_property
from attendance.models import Student, ClassAttendanceWithGeoLocation
from utils.jwt_token_decryption import decode_jwt_token
from . import common


class MarkAttendanceMixin(object):
    @cached_property
    def student(self):
        jwt_token = self.data.get("jwtToken", None)
        if not jwt_token:
            raise exceptions.ParseError(
                {"status": "error", "message": "Please update your app"}
            )

        decoded_data = decode_jwt_token(jwt_token)

        if "error" in decoded_data:
            raise exceptions.ParseError(detail={"message": decoded_data["error"]})

        did = decoded_data["did"]
        try:
            user_obj = Student.objects.get(token=did)
            return user_obj
        except Student.DoesNotExist:
            return None


class MarkAttendanceByGeoPostInputValidator(serializers.Serializer):
    accuracy = serializers.FloatField()
    jwtToken = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    version = serializers.CharField()


class MarkAttendanceByGeoView(
    MarkAttendanceMixin, common.ActiveClassMixin, views.APIView
):
    def post(self, request):
        self.data = request.data
        serializer = MarkAttendanceByGeoPostInputValidator(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not self.student:
            raise exceptions.NotFound({"message": "No such student exists"})
        if not self.active_class:
            raise exceptions.NotFound({"message": "No class active for attendance"})

        ClassAttendanceWithGeoLocation.create_with(
            self.student,
            self.active_class,
            self.data.get("latitude"),
            self.data.get("longitude"),
            self.data.get("accuracy"),
        )
        return Response({"message": "Attendance Marked"}, status=status.HTTP_200_OK)


class MarkAttendanceByBSMView(MarkAttendanceMixin, views.APIView):
    def post(self, request, *args, **kwargs):
        # TODO: Implement logic to mark attendance by BSM
        return Response(status=status.HTTP_200_OK)


class MarkAttendanceByBluetoothView(MarkAttendanceMixin, views.APIView):
    def post(self, request, *args, **kwargs):
        # TODO: Implement logic to mark attendance by Bluetooth
        return Response(status=status.HTTP_200_OK)


class VerifyMarkByGeoLocationView(MarkAttendanceMixin, views.APIView):
    def get(self, request, *args, **kwargs):
        # TODO: Implement logic to verify mark by geo location
        return Response(status=status.HTTP_200_OK)
