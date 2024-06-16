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
    email_list = serializers.ListField(child=serializers.EmailField())


class StudentGroupView(views.APIView):

    def post(self, request, pk, *args, **kwargs):
        validator = AddStudentsInputValidator(data=request.data)
        if not validator.is_valid():
            db_logger.error(f"Validation errors: {validator.errors}")
            return Response(validator.errors, status=400)
        
        group = get_object_or_404(StudentGroup, pk=pk)
        data = validator.validated_data
        
        return Response({'status': 'success', 'data': data}, status=200)

    def get(self, request, pk, *args, **kwargs):
        group = get_object_or_404(StudentGroup, pk=pk)

        return render(request, "attendance/studentGroup.html", {"name": group.name})
