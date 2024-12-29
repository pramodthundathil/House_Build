from django.shortcuts import render,redirect
from .forms import ProductAddForm, ServiceForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ProductDetails,CartItems, CheckoutItems, CheckoutAddress, Review

import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import HttpResponseBadRequest


razorpay_client = razorpay.Client(
  auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

@login_required(login_url="SignIn")
def MerchantProduct(request):
    form = ProductAddForm()
    product = ProductDetails.objects.filter(user = request.user)
    
    if request.method == "POST":
        form = ProductAddForm(request.POST,request.FILES)
        if form.is_valid():
            med  = form.save()
            med.user = request.user
            med.save()
            messages.info(request,"Product added")
            return redirect("MerchantProduct")
        else:
            messages.info(request,"SomeThing Wrong")
            return redirect("MerchantProduct")
    
    context = {
        "form":form,
        "product":product
    }
    return render(request,"merchant/products.html",context)

def delete_product(request,pk):
    product = ProductDetails.objects.get(id =pk)
    product.Product_Image.delete()
    product.delete()
    messages.success(request,"Product deleted success")
    return redirect("MerchantProduct")


def ProductsingleView(request,pk):
    product = ProductDetails.objects.get(id = pk)
    review = Review.objects.filter(product = product)
    cat = product.Product_category
    subcat = product.Product_subcategory

    suggested = ProductDetails.objects.filter(Product_subcategory = subcat, Product_category = cat)

    context = {
        "product":product,
        "suggested":suggested,
        "review":review,
        "lenreview":len(review)
    }
    return render(request,"productsingleview.html",context)



@login_required(login_url='SignIn')
def AddToCart(request,pk):
    product = ProductDetails.objects.get(id = pk)
    try: 
        CartItems.objects.get(product = product)
        item = CartItems.objects.get(product = product)
        item.stock += 1
        item.price += product.product_price
        item.save()
    except:
        cart = CartItems.objects.create(product = product,user = request.user,stock = 1,price = product.product_price )
        cart.save()
    return redirect('Cart')

@login_required(login_url='SignIn')
def IncreaseQuantity(request,pk):
    cart = CartItems.objects.get(id = pk)
    cart.stock = cart.stock + 1
    cart.price = cart.price + cart.product.product_price
    cart.save()
    return redirect('Cart')

@login_required(login_url='SignIn')
def DecreaseQuantity(request,pk):
    cart = CartItems.objects.get(id = pk)
    
    if cart.stock == 1:
        cart.delete()
    else:
        cart.stock = cart.stock - 1
        cart.price = cart.price - cart.product.product_price
        cart.save()
    return redirect('Cart')

@login_required(login_url='SignIn')
def DeleteCartItem(request,pk):
    cart = CartItems.objects.get(id = pk)
    cart.delete()
    return redirect('Cart')
    

@login_required(login_url='SignIn')
def Cart(request):
    cartitems = CartItems.objects.filter(user = request.user)
    total = 0
    for item in cartitems:
        total = total + item.price
    gst = total*18/100
    price = total - gst
    

    context = {
        "cartitems":cartitems,
        "total":total,
        "gst":gst,
        "price":price,
        'lencart':len(cartitems)
    }
    return render(request,"cart.html",context)


def CheckOut(request):
    cartitems = CartItems.objects.filter(user = request.user)
    total = 0
    for item in cartitems:
        total = total + item.price
    gst = total*18/100
    price = total - gst
    

    context = {
        "cartitems":cartitems,
        "total":total,
        "gst":gst,
        "price":price,
        'lencart':len(cartitems)
    }
    return render(request,"checkout.html",context)

@login_required(login_url='SignIn')
def ProceedCheckout(request):
    cart = CartItems.objects.filter(user = request.user)
    if request.method == "POST":
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        email = request.POST["email"]
        mob = request.POST["mob"]
        add1 = request.POST["add1"]
        add2 = request.POST["add2"]
        city = request.POST["city"]
        state = request.POST["state"]
        pin = request.POST["pin"]

        check =  CheckoutAddress.objects.create(firstname = fname,lastname = lname, email = email ,mob = mob , address1 = add1  , address2 = add2 , city = city, state = state, pin = pin, user = request.user )
        check.save()

    for i in cart:
        Checkoutitems = CheckoutItems.objects.create(product = i.product,user=request.user,stock = i.stock,price = i.price,status = "item Ordered", checkoutaaddress = check)
        Checkoutitems.save()
        dcart = CartItems.objects.get(id = i.id)
        dcart.delete()
    checkitems = CheckoutItems.objects.filter(user = request.user,payment_status = False)
    total = 0
    for item in checkitems:
        total = total + item.price
    currency = 'INR'
    amount = total * 100 # Rs. 200
    context = {}

  # Create a Razorpay Order Pyament Integration.....
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                          currency=currency,
                          payment_capture='0'))

  # order id of newly created order.
    razorpay_order_id = razorpay_order["id"]
    callback_url = "paymenthandler/"

  # we need to pass these details to frontend.
    
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url 
    context['slotid'] = "1",
    context['numitems'] = len(checkitems)
    context['total'] = total
    # context['amt'] = (product1.Product_price)*float(qty)
    

    
    return render(request,'checkoutpage.html',context)

@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

      # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is not None:
                checkitems = CheckoutItems.objects.filter(user = request.user,payment_status = False)
                total = 0
                for item in checkitems:
                    total = total + item.price
                    checkitems.payment_status = True
                    checkitems.save()
                amount = total * 100 # Rs. 200
                try:
                    print("working 1")
                    razorpay_client.payment.capture(payment_id, amount)
                    return redirect('Success1')
          # render success page on successful caputre of payment
                except:
                    print("working 2")
                    return redirect('Success1')
                    
                    
          # if there is an error while capturing payment.
            else:
                return render(request, 'paymentfail.html')
        # if signature verification fails.    
        except:
            return HttpResponseBadRequest()
        
      # if we don't find the required parameters in POST data
    else:
  # if other than POST request is made.
        return HttpResponseBadRequest()
    
def Success1(request):
    return render(request,'Paymentconfirm.html')


@login_required(login_url='SignIn')
def MyOrderes(request):
    orderitems = CheckoutItems.objects.filter(user=request.user)
    context = {
        "orderitems":orderitems
    }
    return render(request,'myorders.html',context)

def deleteordermanu(request,pk):
    CheckoutItems.objects.filter(id=pk).delete()
    return redirect("MyOrderes")
    
def deleteordercus(request,pk):
    CheckoutItems.objects.filter(id=pk).delete()
    return redirect("MyOrderes")


def Shop(request):
    product = ProductDetails.objects.all()

    context = {
        "product":product
    }
    return render(request,"shop.html",context)


def CustomerorederMerchant(request):
    check = CheckoutItems.objects.filter(product__user = request.user)
    context = {
        "check":check
    }
    return render(request,"merchant/customerorder.html",context)


def ChangeOrderStatus(request,pk,str):
    items = CheckoutItems.objects.get(id = pk)
    items.status = str
    items.save()
    return redirect("CustomerorederMerchant")

def ViewCustomerAddress(request,pk):
    it = CheckoutItems.objects.get(id = pk)
    items = it.checkoutaaddress
    context = {
        "items":items
    }
    return render(request, "merchant/customer.html",context)


def Sorting(request,str):
    product = ProductDetails.objects.filter(Product_subcategory = str)
    context = {
        "product":product
    }
    return render(request,"shop.html",context)

def Sorting1(request,str):
    product = ProductDetails.objects.filter(Product_category = str)
    context = {
        "product":product
    }
    return render(request,"shop.html",context)


def Search(request):
    if request.method == "POST":
        search = request.POST['search']
        product = ProductDetails.objects.filter(product_name__contains = search)
        context = {
        "product":product
        }
        return render(request,"shop.html",context)
    
@login_required(login_url='SignIn')
def Addreviews(request,pk):
    prod = ProductDetails.objects.get(id = pk)
    if request.method == "POST":
        review = request.POST["review"]
        name = request.POST["name"]

        review = Review.objects.create(name = name, review = review, user = request.user, product = prod)
        review.save()
        return redirect("ProductsingleView",pk= pk)


def ProducteditMercahant(request,pk):
    product = ProductDetails.objects.get(id = pk)
    if request.method == "POST":
        name = request.POST['name']
        price = request.POST['price']
        dis = request.POST['dis']
        stock = request.POST['stock']

        product.product_name = name 
        product.product_price = price
        product.product_description = dis
        product.product_stock = stock
        product.save()
        messages.info(request,"Product Updated..")
        return redirect("ProducteditMercahant",pk= pk)
    
    context = {
        "product":product
    }
    return render(request,"merchant/merchantproductsingleview.html",context)

def ChangeImage(request,pk):
    product = ProductDetails.objects.get(id = pk)
    if request.method == "POST":
        image = request.FILES['image']
        product.Product_Image.delete()
        product.Product_Image = image
        product.save()
        messages.info(request,"Product Updated..")
        return redirect("ProducteditMercahant",pk= pk)
    


# service functions 

from .models import Service, ServiceBooking
@login_required(login_url="SignIn")
def service_merchant(request):
    form = ServiceForm()
    services = Service.objects.filter(user = request.user)
    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.user = request.user
            form.save()
            messages.success(request,"Service added...")
            return redirect(service_merchant)
        else:
            messages.error(request,"Service not added...")
            return redirect(service_merchant)


    context = {
        "form":form,
        "services":services
    }
    return render(request,'merchant/services.html',context)


def ServiceEdit(request,pk):
    services = Service.objects.get(id = pk)
    form = ServiceForm(instance=services)
    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES,instance=services)
        if form.is_valid():
            form.save()
            messages.success(request,"Service added...")
            return redirect("service_merchant")
        else:
            messages.error(request,"Service not added...")
            return redirect(service_merchant)

    return render(request,'merchant/services_edit.html',{"form":form})


def delete_service(request,pk):
    services = Service.objects.get(id = pk)
    services.image.delete()
    services.delete()
    messages.success(request,"Service deleted...")
            
    return redirect(service_merchant)

def services(request):
    services = Service.objects.all()

    context = {
       "services":services 
    }
    return render(request,"services.html",context)

from .forms import ServiceBookingForm

@login_required(login_url="SignIn")
def book_appointment(request,pk):
    services = Service.objects.get(id = pk)
    form = ServiceBookingForm()
    if request.method == 'POST':
        # Get form data from request
        # appointment_date = request.POST.get('appointment_date')
        # appointment_time = request.POST.get('appointment_time')
        # notes = request.POST.get('notes')

        # apmnt = ServiceBooking.objects.create(customer = request.user, service = services, appointment_date = appointment_date, appointment_time = appointment_date,notes = notes)
        # apmnt.save()
        # messages.info(request,"booking Success")
        # return redirect("services")
        form = ServiceBookingForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.service =  services
            data.customer = request.user
            data.save()
            messages.info(request,"booking Success")
            return redirect("services")
    return render(request,"book_appointment.html",{"form":form})

@login_required(login_url="SignIn")
def booked_services(request):
    bookings = ServiceBooking.objects.filter(customer = request.user)
    return render(request,"bookedservices.html",{"bookings":bookings})

    




