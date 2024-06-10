from dashboard.models import Doctype, School, Topic, Transaction


def dashboard(request):
    user = request.user
    if request.user.is_authenticated:
        student = user.student
        transactions = Transaction.objects.filter(user=student)
        upload_trans = transactions.filter(transaction_type="upload")
        purchase_trans = transactions.filter(transaction_type="purchase")
        points = student.points_field
        doctypes = Doctype.objects.all().order_by('name')
        schools = School.objects.all().order_by('name')
        topics = Topic.objects.all().order_by('name')
        purch_amount=0
        upload_amount=0
        for transaction in purchase_trans:
            purch_amount += transaction.amount
        for transaction in upload_trans:
            upload_amount += transaction.amount
        context = {
            'user': user,
            'student': student,
            'points': points,
            'doctypes': doctypes,
            'schools': schools,
            'topics': topics,
            'transactions': transactions,
            'upload_amount': upload_amount,
            'purch_amount': purch_amount
        }
        return context
    return {}
