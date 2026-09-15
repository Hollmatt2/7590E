"""The web addresses of the Calder app, and the view in core/views.py that handles each one."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("queue/", views.work_queue, name="work_queue"),
    path("reports/", views.reports, name="reports"),
    path("agreements/new/", views.submit_agreement, name="submit_agreement"),
    path("agreements/mine/", views.my_submissions, name="my_submissions"),
    path("agreements/<int:pk>/", views.agreement_detail, name="agreement_detail"),
    path("agreements/<int:pk>/document/", views.agreement_document, name="agreement_document"),
    path("agreements/<int:pk>/identify/", views.identify, name="identify"),
    path("agreements/<int:pk>/identify/finish/", views.finish_identification, name="finish_identification"),
    path("agreements/<int:pk>/findings/<int:flag_pk>/remove/", views.remove_finding, name="remove_finding"),
    path("agreements/<int:pk>/findings/<int:flag_pk>/decide/", views.decide_flag, name="decide_flag"),
    path("agreements/<int:pk>/review/", views.review, name="review"),
    path("agreements/<int:pk>/review/outcome/", views.dispose, name="dispose"),
    path("agreements/<int:pk>/review/add/", views.add_missed_finding, name="add_missed_finding"),
]
