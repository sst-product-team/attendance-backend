from django.utils.functional import cached_property
from attendance.models import SubjectClass


class ActiveClassMixin(object):
    @cached_property
    def active_class(self):
        return SubjectClass.get_current_class()
