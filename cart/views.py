from audioop import reverse

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.html import format_html

from .cart import Cart
from dashboard.models import Document, Student, Transaction
from django.http import JsonResponse


def cart_summary(request):
    user = request.user.student
    cart = Cart(request)
    cart_docs = cart.get_docs()
    print(cart_docs)
    total = cart.cart_total()
    points = user.points_field
    context = {
        'segment': 'cart',
        'cart_docs': cart_docs,
        'total': total,
        'points': points

    }
    return render(request, 'cart/cart_summary.html', context)


def cart_add(request):
    cart = Cart(request)
    student = request.user.student
    if request.POST.get('action') == 'post':
        document_id = int(request.POST.get('document_id'))
        document = get_object_or_404(Document, id=document_id)
        if document not in student.purchased_documents.all():
            cart.add(document=document)
        # Get Cart Quantity
        cart_quantity = cart.__len__()

        # Return resonse
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request,
                         "Added Succesfully To Cart!")
        return response


def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # Get stuff
        document_id = int(request.POST.get('document_id'))
        document = get_object_or_404(Document, id=document_id)
        # Call delete Function in Cart
        cart.delete(document=document)

        response = JsonResponse({'document': document_id})
        # return redirect('cart_summary')
        messages.success(request, ("Item Deleted From Shopping Cart..."))
        return response


def make_payment(request):
    if request.method == 'POST':
        student = request.user.student
        cart = Cart(request)
        cart_docs = cart.get_docs()
        total = cart.cart_total()
        points = student.points_field
        if not cart_docs:
            messages.warning(request, 'Your cart is empty.')
            return redirect(request.META.get('HTTP_REFERER'))
        if total <= points:
            cost = 0
            for doc in cart_docs:
                if doc not in student.purchased_documents.all():
                    student.purchased_documents.add(doc)
                    cost += doc.cost
                    Transaction.objects.create(
                        user=student,
                        document=doc,
                        transaction_type='purchase',
                        amount=doc.cost
                    )
            student.points_field -= cost
            student.save()
            cart.clear()
            messages.success(request, 'Documents added to your library!')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'You do not have enough points. Please buy more points.')
            return redirect(request.META.get('HTTP_REFERER'))
