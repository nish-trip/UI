import requests
import json
from pprint import pprint

customers = requests.get("https://demo2.transo.in/api/trip/getCustomerList").json()["data"]
customer_list = [x["customer_company"] for x in customers]
branches = requests.get("https://demo2.transo.in/api/trip/getSubBranchList").json()["data"]
branch_list = [x["warehouse_name"] for x in branches]


customer_name = "AKSHATHA TRANSPORT"
sub_branch_name = "Indiranagar"
booking_date = "2021-05-28"
data_dict = {"customer_name":customer_name,"sub_branch_name": sub_branch_name,"actual_booking_date": booking_date}
data = json.dumps(data_dict)

headers = {'content-type': "application/json"}
receipt = requests.post("https://demo2.transo.in/api/trip/LrNumberDetails", headers=headers, data = data).json()["data"]
lr_number = ["TORVI/LR/20/108","TORVI/LR/20/109"]

trip_id = []
for row in receipt:
    if row["customer_lr_number"] in lr_number:
        trip_id.append(row["trip_consignment_id"])


lr_list = []
for i in range(len(trip_id)):
    temp_dict = {"customer_lr_number":lr_number[i], "trip_consignment_id":trip_id[0]}
    lr_list.append(temp_dict)

payload_dict = {"actual_dispatch_date":"2021-05-28", "lr_list":lr_list}

payload = json.dumps(payload_dict)

obj = requests.post("https://demo2.transo.in/api/trip/UpdateShipmentDispatchDate", headers=headers, data = payload)
if obj.ok:
    print(obj.json()["message"])
else:
    print("failed")