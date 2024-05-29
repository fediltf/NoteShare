from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from .cart import Cart
from dashboard.models import Document, Student
from django.http import JsonResponse


def cart_summary(request):
    user = request.user.student
    cart = Cart(request)
    cart_docs = cart.get_docs()
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
    if request.POST.get('action') == 'post':
        document_id = int(request.POST.get('document_id'))
        document = get_object_or_404(Document, id=document_id)
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


def cart_update(request):
    pass
