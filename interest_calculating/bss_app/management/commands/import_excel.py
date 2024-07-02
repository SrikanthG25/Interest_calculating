import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from bss_app.models import BookingPaymentSchedule, PaymentReceiptMaster, PaymentReceiptReferences, CreditsNotesMaster, CreditsNotesReferences

class Command(BaseCommand):
    help = 'Import data from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='The path to the Excel file')

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']

        try:    
            df = pd.read_excel(excel_file, engine='openpyxl')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading Excel file: {e}"))
            return

        self.stdout.write(f"Columns found in Excel file: {df.columns}")

        def clean_numeric(value):
            if isinstance(value, str):
                return float(''.join(filter(str.isdigit, value)))
            else:
                return float(value)

        for index, row in df.iterrows():
            try:
                booking = BookingPaymentSchedule.objects.create(
                    flat_no=row.get('Flat No.'),
                    customer_code=row.get('Customer Code'),
                    customer_name=row.get('Customer Name.', ''),
                    stage_name=row.get('Description', ''),
                    due_date=datetime.strptime(row.get('Due Date', ''), '%d/%m/%Y').date(),
                    total_amount=float(row.get('Due Amount', 0)),
                    percentage=clean_numeric(row.get('Percentage', 0)),
                )

                if row.get('Receipt Type') == 'Receipt':
                    receipt_master = PaymentReceiptMaster.objects.create(
                        booking=booking,
                        transaction_date=datetime.strptime(row.get('Received  Date', ''), '%d/%m/%Y').date(),
                        customer_code=row.get('Customer Code')
                    )

                    PaymentReceiptReferences.objects.create(
                        receipt_master=receipt_master,
                        amount=float(row.get('Amount Received', 0))
                    )

                elif row.get('Receipt Type') == 'TDS':
                    credits_master = CreditsNotesMaster.objects.create(
                        booking=booking,
                        transaction_date=datetime.strptime(row.get('Received  Date', ''), '%d/%m/%Y').date(),
                        customer_code=row.get('Customer Code')
                    )

                    CreditsNotesReferences.objects.create(
                        credits_notes_master=credits_master,
                        amount=float(row.get('Amount Received', 0))
                    )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing row {index}: {e}"))

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))