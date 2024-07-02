import math
from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.response import Response
from datetime import datetime
from .models import BookingPaymentSchedule, PaymentReceiptReferences, CreditsNotesReferences
import xlsxwriter
import logging

logger = logging.getLogger(__name__)

class InterestReportView(generics.GenericAPIView):
    def get(self, request):
        try:
            data = request.GET
            flat_no = data.get('flat_no')
            customer_code = data.get('customer_code')
            
            bookings = BookingPaymentSchedule.objects.all()
            
            report_data = self.calculate_interest(bookings)
            
            return Response({'status': 'success', 'message': 'Interest Report', 'data': report_data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception('Exception occurred: {}'.format(e))
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def calculate_interest(self, bookings):
        report_data = []
        
        for s, booking in enumerate(bookings, start=1):
            due_date = booking.due_date
            due_amount = booking.total_amount

            receipts = PaymentReceiptReferences.objects.filter(receipt_master__booking_id=booking.id)
            credits = CreditsNotesReferences.objects.filter(credits_notes_master__booking_id=booking.id)

            total_received = sum([receipt.amount for receipt in receipts]) if receipts else sum([credit.amount for credit in credits])
            
            received_date = receipts[0].receipt_master.transaction_date if receipts else (credits[0].credits_notes_master.transaction_date if credits else None)
            specific_date = datetime.strptime('20/06/2024', '%d/%m/%Y').date()
            no_of_delays = (due_date - (received_date if received_date else specific_date) ).days
            if no_of_delays > 0:
                no_of_day = 0
            else:
                no_of_day = abs(no_of_delays)
            if no_of_delays < 0:
                interest = ((total_received * no_of_delays * 0.1025) / 365) if total_received > 0 else ((due_amount * no_of_delays * 0.1025) / 365)
            else:
                interest = 0
            interest = abs(interest)
            gst = math.ceil(interest * 0.18)
            gst = interest * 0.18
            total_interest = interest + gst

            receipt_value = 'Receipt' if receipts.exists() else ('TDS' if credits.exists() else '-')

            description = f'{booking.stage_name}' if booking.stage_name else ''

            report_data.append({
                # 'S_No': s,
                'id':booking.id,
                'Flat_No.': booking.flat_no,
                'Customer_Code': booking.customer_code,
                'Customer_Name': booking.customer_name,
                'Description': description,
                'Due_Date': due_date.strftime('%d/%m/%Y'),
                'Due_Amount': abs(int(due_amount)),
                'Received_Date': received_date.strftime('%d/%m/%Y') if received_date else specific_date,
                'Receipt_Type': receipt_value,
                'Amount_Received': int(total_received),
                'No_of_Delays': no_of_day,
                'Percentage': f'{booking.percentage}%',
                'Interest': round(interest),
                'GST_@_18%': int(gst),
                'Total_Interest': math.ceil(total_interest)
            })
        return report_data


class ExportToExcelView(generics.GenericAPIView):
    def get(self, request):
        try:
            data = request.GET
            flat_no = data.get('flat_no')
            customer_code = data.get('customer_code')
            
            search_data = {}
            if flat_no:
                search_data['flat_no'] = flat_no
            if customer_code:
                search_data['customer_code'] = customer_code

            bookings = BookingPaymentSchedule.objects.filter(**search_data)
            report_data = InterestReportView().calculate_interest(bookings)

            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=interest_report.xlsx'
            
            workbook = xlsxwriter.Workbook(response, {'in_memory': True})
            worksheet = workbook.add_worksheet()

            headers = ['S.No', 'Flat No.', 'Customer Code', 'Customer Name', 'Description', 'Due Date', 'Due Amount', 'Received Date', 'Receipt Type', 'Amount Received', 'No. of Delays', 'Percentage', 'Interest', 'GST @ 18%', 'Total Interest']
            for col_num, header in enumerate(headers):
                worksheet.write(0, col_num, header)
            
            for row_num, row_data in enumerate(report_data, start=1):
                for col_num, (key, value) in enumerate(row_data.items()):
                    worksheet.write(row_num, col_num, value)

            workbook.close()
            return response
        except Exception as e:
            logger.exception('Exception occurred: {}'.format(e))
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)