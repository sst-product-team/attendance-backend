from attendance.models import Student, StudentGroup
from rest_framework import views, serializers
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
import logging

db_logger = logging.getLogger("db")


class AddStudentsInputValidator(serializers.Serializer):
    email_list = serializers.ListField(child=serializers.EmailField())


class StudentGroupView(views.APIView):
    def post(self, request, pk, *args, **kwargs):
        validator = AddStudentsInputValidator(data=request.data)
        if not validator.is_valid():
            db_logger.error(f"Validation errors: {validator.errors}")
            return Response(validator.errors, status=400)

        if not Student.can_add_student_to_group(request):
            return Response(
                {
                    "message": "You are not authorized to access this page",
                    "status": "error",
                },
                status=403,
            )

        group = get_object_or_404(StudentGroup, pk=pk)
        student_emails = validator.validated_data["email_list"]

        success, message = group.add_students_to_group(student_emails)

        if success:
            return Response(
                {"status": "success" if success else "error", "data": message},
                status=201,
            )
        else:
            return Response(
                {"status": "success" if success else "error", "data": message},
                status=207,
            )

    def get(self, request, pk, *args, **kwargs):
        group = get_object_or_404(StudentGroup, pk=pk)

        return render(request, "attendance/studentGroup.html", {"name": group.name})
