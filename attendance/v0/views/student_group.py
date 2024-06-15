from attendance.models import ClassAttendanceByBSM, Student, SubjectClass, StudentGroup
from rest_framework import views, exceptions, serializers
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

db_logger = logging.getLogger("db")


class AddStudentsInputValidator(serializers.Serializer):
    student_group_pk = serializers.IntegerField()
    email_list = serializers.ListField(child=serializers.EmailField())


class StudentGroupView(views.APIView):

    @csrf_exempt
    def post(self, request):
        validator = AddStudentsInputValidator(data=request.data)
        if validator.is_valid():
            data = validator.validated_data
            # Your processing logic here
            # For example, you can log the validated data
            db_logger.info(f"Validated data: {data}")
            return Response({'status': 'success', 'data': data}, status=200)
        else:
            db_logger.error(f"Validation errors: {validator.errors}")
            return Response(validator.errors, status=400)

    def get(self, request, *args, **kwargs):
        student_groups = StudentGroup.objects.all()
        return render(request, "attendance/studentGroup.html", {"student_groups": student_groups})


