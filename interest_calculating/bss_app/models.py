from django.db import models

class BookingPaymentSchedule(models.Model):
    flat_no = models.CharField(max_length=20)
    customer_code = models.CharField(max_length=20)
    customer_name = models.CharField(max_length=100)
    stage_name = models.CharField(max_length=100)
    percentage = models.FloatField()
    due_date = models.DateField()
    total_amount = models.FloatField()

class PaymentReceiptMaster(models.Model):
    booking = models.ForeignKey(BookingPaymentSchedule, on_delete=models.CASCADE)
    transaction_date = models.DateField()
    customer_code = models.CharField(max_length=20)

class PaymentReceiptReferences(models.Model):
    receipt_master = models.ForeignKey(PaymentReceiptMaster, on_delete=models.CASCADE)
    amount = models.FloatField()

class CreditsNotesMaster(models.Model):
    booking = models.ForeignKey(BookingPaymentSchedule, on_delete=models.CASCADE)
    transaction_date = models.DateField()
    customer_code = models.CharField(max_length=20)

class CreditsNotesReferences(models.Model):
    credits_notes_master = models.ForeignKey(CreditsNotesMaster, on_delete=models.CASCADE)
    amount = models.FloatField()