from django.urls import path
from .views import *

urlpatterns = [
    path('report/', InterestReportView.as_view(), name='generate_report'),
    path('report/export/', ExportToExcelView.as_view(), name='export_to_excel'),
]
