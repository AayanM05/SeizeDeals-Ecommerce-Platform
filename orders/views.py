from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
import razorpay


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()


        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)





# # def place_order(request, total=0, quantity=0,):
#     current_user = request.user

#     # If the cart count is less than or equal to 0, then redirect back to shop
#     cart_items = CartItem.objects.filter(user=current_user)
#     cart_count = cart_items.count()
#     if cart_count <= 0:
#         return redirect('store')

#     grand_total = 0
#     tax = 0
#     for cart_item in cart_items:
#         total += (cart_item.product.price * cart_item.quantity)
#         quantity += cart_item.quantity
#     tax = (2 * total)/100
#     grand_total = total + tax

#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             # Store all the billing information inside Order table
#             data = Order()
#             data.user = current_user
#             data.first_name = form.cleaned_data['first_name']
#             data.last_name = form.cleaned_data['last_name']
#             data.phone = form.cleaned_data['phone']
#             data.email = form.cleaned_data['email']
#             data.address_line_1 = form.cleaned_data['address_line_1']
#             data.address_line_2 = form.cleaned_data['address_line_2']
#             data.country = form.cleaned_data['country']
#             data.state = form.cleaned_data['state']
#             data.city = form.cleaned_data['city']
#             data.order_note = form.cleaned_data['order_note']
#             data.order_total = grand_total
#             data.tax = tax
#             data.ip = request.META.get('REMOTE_ADDR')
#             data.save()
#             # Generate order number
#             yr = int(datetime.date.today().strftime('%Y'))
#             dt = int(datetime.date.today().strftime('%d'))
#             mt = int(datetime.date.today().strftime('%m'))
#             d = datetime.date(yr,mt,dt)
#             current_date = d.strftime("%Y%m%d") #20210305
#             order_number = current_date + str(data.id)
#             data.order_number = order_number
#             data.save()

#             order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
#             context = {
#                 'order': order,
#                 'cart_items': cart_items,
#                 'total': total,
#                 'tax': tax,
#                 'grand_total': grand_total,
#             }
#             return render(request, 'orders/payments.html', context)
#     else:
#         return redirect('checkout')
    


def place_order(request, total=0, quantity=0):
    current_user = request.user

    # If cart is empty, redirect to store
    cart_items = CartItem.objects.filter(user=current_user)
    if not cart_items.exists():
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Save Order details
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            current_date = datetime.date.today().strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

            # ✅ Razorpay Payment Integration
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            amount_in_paise = int(grand_total * 100)  # Razorpay needs amount in paise

            razorpay_order = client.order.create({
                "amount": amount_in_paise,
                "currency": "INR",
                "payment_capture": "1"
            })

            order.razorpay_order_id = razorpay_order['id']
            order.save()

            # Send this data to payments.html
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
                'currency': 'INR',
                'callback_url': '/orders/paymenthandler/',  # this URL handles the Razorpay response
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')



# def order_complete(request):
#     order_number = request.GET.get('order_number')
#     transID = request.GET.get('payment_id')

#     try:
#         order = Order.objects.get(order_number=order_number, is_ordered=True)
#         ordered_products = OrderProduct.objects.filter(order_id=order.id)

#         subtotal = 0
#         for i in ordered_products:
#             subtotal += i.product_price * i.quantity

#         payment = Payment.objects.get(payment_id=transID)

#         context = {
#             'order': order,
#             'ordered_products': ordered_products,
#             'order_number': order.order_number,
#             'transID': payment.payment_id,
#             'payment': payment,
#             'subtotal': subtotal,
#         }
#         return render(request, 'orders/order_complete.html', context)
#     except (Payment.DoesNotExist, Order.DoesNotExist):
#         return redirect('home')

from django.contrib import messages  # add this at the top

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        # ✅ Show success message
        messages.success(request, "Your order has been placed successfully!")

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')



# @csrf_exempt
# def paymenthandler(request):
#     if request.method == "POST":
#         try:
#             # Razorpay client setup
#             client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

#             # Get the payment data from Razorpay
#             payment_id = request.POST.get('razorpay_payment_id', '')
#             order_id = request.POST.get('razorpay_order_id', '')
#             signature = request.POST.get('razorpay_signature', '')

#             # Verify the payment signature
#             params_dict = {
#                 'razorpay_order_id': order_id,
#                 'razorpay_payment_id': payment_id,
#                 'razorpay_signature': signature
#             }

#             result = client.utility.verify_payment_signature(params_dict)
            
#             if result is None:
#                 # Payment is successful and verified
#                 # You should mark the order as paid here
#                 order = Order.objects.get(order_number=order_id)

#                 order.payment_id = payment_id
#                 order.is_ordered = True
#                 order.status = "Paid"
#                 order.save()

#                 # You can create OrderProduct instances here if needed

#                 return render(request, 'orders/order_complete.html', {'order': order})
#             else:
#                 return HttpResponseBadRequest("Signature verification failed.")
#         except Exception as e:
#             print("Exception in paymenthandler:", e)
#             return HttpResponseBadRequest("Something went wrong.")
#     else:
#         return HttpResponseBadRequest("Invalid request.")



@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            # Razorpay client setup
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Get the payment data from Razorpay
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')

            # Verify the payment signature
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            
            print("POST Data:", request.POST)

            client.utility.verify_payment_signature(params_dict)

            # ✅ Corrected: Match the razorpay_order_id field from your Order model
            order = Order.objects.get(razorpay_order_id=order_id)


            # Update order with payment details
            order.is_ordered = True
            order.status = "Accepted"
            order.save()
            
            print("Received from Razorpay:", order_id)
            print("Order IDs in DB:", list(Order.objects.values_list('razorpay_order_id', flat=True)))


            # You can optionally save the Payment instance or OrderProduct entries here

            return render(request, 'orders/order_complete.html', {'order': order})

        except Order.DoesNotExist:
            print("Order not found for Razorpay Order ID:", order_id)
            return HttpResponseBadRequest("Order matching query does not exist.")
        except Exception as e:
            print("Exception in paymenthandler:", e)
            return HttpResponseBadRequest("Something went wrong.")
    else:
        return HttpResponseBadRequest("Invalid request.")





@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            razorpay_order_id = data.get("razorpay_order_id")
            razorpay_payment_id = data.get("razorpay_payment_id")
            razorpay_signature = data.get("razorpay_signature")

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Signature verification
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            try:
                client.utility.verify_payment_signature(params_dict)
                # Update order status
                # order = Order.objects.get(order_number=razorpay_order_id, is_ordered=False)
                # order.is_ordered = True
                # order.payment_id = razorpay_payment_id
                # order.status = 'Completed'
                # order.save()
                # Get the order
                order = Order.objects.get(razorpay_order_id=razorpay_order_id, is_ordered=False)

                # Create Payment object
                payment = Payment.objects.create(
                    user=request.user,
                    payment_id=razorpay_payment_id,
                    payment_method="Razorpay",
                    amount_paid=order.order_total,
                    status='Completed',
                )

                # Mark order as complete
                order.payment = payment
                order.is_ordered = True
                order.status = 'Completed'
                order.save()

                # Move cart items to OrderProduct
                cart_items = CartItem.objects.filter(user=request.user)
                for item in cart_items:
                    order_product = OrderProduct.objects.create(
                        order=order,
                        payment=payment,
                        user=request.user,
                        product=item.product,
                        quantity=item.quantity,
                        product_price=item.product.price,
                        ordered=True
                    )
                    order_product.variations.set(item.variations.all())
                    order_product.save()

                    # Reduce stock
                    product = Product.objects.get(id=item.product.id)
                    product.stock -= item.quantity
                    product.save()

                # Clear cart
                CartItem.objects.filter(user=request.user).delete()

                # Send order confirmation email
                mail_subject = 'Thank you for your order!'
                message = render_to_string('orders/order_recieved_email.html', {
                    'user': request.user,
                    'order': order,
                })
                to_email = request.user.email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.send()


                # Reduce stock & move cart items to OrderProduct
                # (optional: you can move this logic here)

                return JsonResponse({'status': 'success'})
            except razorpay.errors.SignatureVerificationError:
                return JsonResponse({'status': 'fail', 'reason': 'Invalid signature'})

        except Exception as e:
            return JsonResponse({'status': 'fail', 'reason': str(e)})

    return JsonResponse({'status': 'fail', 'reason': 'Invalid request'})



