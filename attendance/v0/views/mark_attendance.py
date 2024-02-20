from attendance.models import ClassAttendanceByBSM
import rest_framework
from django.views.decorators.csrf import csrf_exempt
from rest_framework import views
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework import serializers
from attendance.models import Student, SubjectClass
import json
from django.shortcuts import render
from django.shortcuts import get_object_or_404
import logging

db_logger = logging.getLogger("db")


class MailStatusSerializer(serializers.Serializer):
    mail = serializers.EmailField()
    status_choices = ["present", "absent", "proxy"]
    status = serializers.ChoiceField(choices=status_choices)


class MarkAttendanceByGeoPostInputValidator(serializers.Serializer):
    accuracy = serializers.FloatField()
    jwtToken = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    version = serializers.CharField()


# class MarkAttendanceByGeoView(
#    MarkAttendanceMixin, common.ActiveClassMixin, views.APIView
# ):
#    def post(self, request):
#        self.data = request.data
#        serializer = MarkAttendanceByGeoPostInputValidator(data=request.data)
#        serializer.is_valid(raise_exception=True)
#
#        if not self.student:
#            raise exceptions.NotFound({"message": "No such student exists"})
#        if not self.active_class:
#            raise exceptions.NotFound({"message": "No class active for attendance"})
#
#        ClassAttendanceWithGeoLocation.create_with(
#            self.student,
#            self.active_class,
#            self.data.get("latitude"),
#            self.data.get("longitude"),
#            self.data.get("accuracy"),
#        )
#        return Response({"message": "Attendance Marked"}, status=status.HTTP_200_OK)


class BulkMarkAttendanceByBSMView(views.APIView):
    def post(self, request, pk, *args, **kwargs):
        if not Student.can_mark_attendance(request):
            return Response(
                {
                    "message": "You are not authorized to access this page",
                    "status": "error",
                },
                status=403,
            )

        serializer = MailStatusSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.data = request.data

        db_logger.info(
            f"""[Bulk Mark Attendance]
by: {request.user.email},
body: {json.dumps(request.data)},
url: {request.build_absolute_uri()}"""
        )

        subject = SubjectClass.objects.filter(pk=pk)
        if not subject.exists():
            raise exceptions.NotFound({"message": "Class not found"})
        else:
            subject = subject.first()

        response = []
        for mailstatus in self.data:
            mail, status = mailstatus["mail"], mailstatus["status"]
            student = get_object_or_404(Student, mail=mail)

            bsm_attendance = ClassAttendanceByBSM.create_with(
                student, subject, status, request.user
            )
            response.append(
                {
                    "mail": mail,
                    "status": bsm_attendance.class_attendance.attendance_status.name,
                }
            )
        return Response(response, status=rest_framework.status.HTTP_200_OK)

    def get(self, request, pk, *args, **kwargs):
        return render(request, "attendance/index.html")
