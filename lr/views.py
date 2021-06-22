from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Receipt
from django.contrib.auth.decorators import login_required
import requests
import json
import re

l1 = []

def home(request):

    return render(request, 'index.html', {"title": "Home"}) 

def register(request): 

    if request.method == 'POST': 
        email = request.POST['email'] 
        username = request.POST['username']
        password1 = request.POST['password']
        password2 = request.POST['confirm'] 

        if password1 == password2:
            if User.objects.filter(username=username).exists(): 
                messages.info(request, 'username already taken')
                return redirect('register')
            
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'email already taken')
                return redirect('register')

            else:
                user = User.objects.create_user(email=email, username=username, password=password1)
                user.save()
                print(f"user created with username : {username}")
                return redirect("/")
        else:
            messages.info(request, 'passwords do not match')
            return redirect('register') 
        

    else:         
        return render(request, 'register.html', {"title": "Register"}) 

def login(request):
    if request.method == "POST": 
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password) 

        if user is not None:
            auth.login(request,user)
            return redirect('/')
        
        else:
            messages.info(request, "invalid credentials")
            return redirect('login')

    else:
        return render(request, 'login.html', {"title": "Login"})

@login_required(login_url='login')
def customer(request):

    if request.method == "POST" and request.POST["button"] == "search":
        ##### perform form processing in this function

        print("search button clicked",'\n')
        # passing customer_list and branch_list to customer.html
        branches = requests.get("https://demo2.transo.in/api/trip/getSubBranchList").json()["data"]
        branch_list = [x["warehouse_name"] for x in branches]
        customers = requests.get("https://demo2.transo.in/api/trip/getCustomerList").json()["data"]
        customer_list = [x["customer_company"] for x in customers]
       
        # on clicking search retrieve the value of these 3 var from the template
        customer_name = f"{request.POST['customer_detail']}"
        l1.append(customer_name)
        sub_branch_name = f"{request.POST['sub-branch']}"
        l1.append(sub_branch_name)
        booking_date = f"{request.POST['booking-date']}"
        l1.append(booking_date)
        
        payload_dict = {"customer_name":customer_name,"sub_branch_name": sub_branch_name,"actual_booking_date": booking_date}
        payload = json.dumps(payload_dict) 

        headers = {'content-type': "application/json"}
        # receipt is a list of dictionaries
        receipt = requests.post("https://demo2.transo.in/api/trip/LrNumberDetails", headers=headers, data = payload).json()["data"]
        
        return render(request, "customer.html", {"title": "LR", "branch_list": branch_list, "customer_list": customer_list, "receipt_list": receipt})


    elif request.method == "POST" and request.POST["button"] == "submit":

        '''request.POST = {'csrfmiddlewaretoken': ['qVrPBg4VnzxaAFEzZJfFUBvXhHuROGXorSpPpjvl2X1SPYDKEFKKDDXATVhkiVmX'], 
        'lr_number': ['TORVI/LR/20/108', 'TORVI/LR/20/109'], 'shipment-date': ['2021-06-24'], 'button': ['submit']}'''

        print("submit button clicked",'\n')

        branches = requests.get("https://demo2.transo.in/api/trip/getSubBranchList").json()["data"]
        branch_list = [x["warehouse_name"] for x in branches]
        customers = requests.get("https://demo2.transo.in/api/trip/getCustomerList").json()["data"]
        customer_list = [x["customer_company"] for x in customers]

        customer_name = l1[0]
        sub_branch_name = l1[1]
        booking_date = l1[2]
        data_dict = {"customer_name":customer_name,"sub_branch_name": sub_branch_name,"actual_booking_date": booking_date}
        data = json.dumps(data_dict)

        headers = {'content-type': "application/json"}
        receipt = requests.post("https://demo2.transo.in/api/trip/LrNumberDetails", headers=headers, data = data).json()["data"]
        lr_number = request.POST['lr_number']

        trip_id = []
        for row in receipt:
            if row["customer_lr_number"] in lr_number:
                trip_id.append(row["trip_consignment_id"])

        lr_list = []
        for i in range(len(trip_id)):
            temp_dict = {"customer_lr_number":lr_number[i], "trip_consignment_id":trip_id[i]}
            lr_list.append(temp_dict)

        actual_dispatch_date = "2021-05-28"
        #actual_dispatch_date = request.POST['shipment-date']

        payload_dict = {"actual_dispatch_date":"2021-05-28", "lr_list":lr_list}             
        payload = json.dumps(payload_dict)

        obj = requests.post("https://demo2.transo.in/api/trip/UpdateShipmentDispatchDate", headers=headers, data = payload)

        if obj.ok:
            print(obj.json()["message"])
            return redirect('/')
        else:
            print("ERROR while trying to make the changes")
            return render(request, "customer.html", {"title": "Customer", "branch_list": branch_list, "customer_list": customer_list, "receipt_list": []})
            
    elif request.method == "POST" and request.POST["button"] == "cancel":

        print("changes cancelled")
        branches = requests.get("https://demo2.transo.in/api/trip/getSubBranchList").json()["data"]
        branch_list = [x["warehouse_name"] for x in branches]

        customers = requests.get("https://demo2.transo.in/api/trip/getCustomerList").json()["data"]
        customer_list = [x["customer_company"] for x in customers]
        return render(request, "customer.html", {"title": "Refreshed", "branch_list": branch_list, "customer_list": customer_list, "receipt_list": []})

    else:
        print("running GET method ")
        branches = requests.get("https://demo2.transo.in/api/trip/getSubBranchList").json()["data"]
        branch_list = [x["warehouse_name"] for x in branches]

        customers = requests.get("https://demo2.transo.in/api/trip/getCustomerList").json()["data"]
        customer_list = [x["customer_company"] for x in customers]
        
        return render(request, "customer.html", {"title": "Customer", "branch_list": branch_list, "customer_list": customer_list, "receipt_list": []})
