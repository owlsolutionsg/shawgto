import requests
import datetime
import csv
from collections import defaultdict
import paramiko

# Constants
API_TOKEN = ""
STORE_ID = ""
SFTP_HOST = "pos.shawplaza.sg"
SFTP_PORT = 22
SFTP_USERNAME = ""
SFTP_PASSWORD = ""
SFTP_UPLOAD_PATH = ""
LOCAL_SAVE_PATH = "/home/xxxx/"

# Headers for Loyverse API
headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

def fetch_sales_data(start_time, end_time):
    url = "https://api.loyverse.com/v1.0/receipts"
    params = {
        "created_at_min": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z",
        "created_at_max": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z",
        "limit": 250  # Adjust as needed for large data sets
    }
    all_receipts = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        all_receipts.extend(data.get("receipts",[]))
        if "cursor" not in data:
           break
        params["cursor"] = data["cursor"]
    return {"receipts": all_receipts}

def process_sales_data(receipts):
    hourly_sales = defaultdict(lambda: {
        "count": 0,
        "total_sales": 0.0
    })
    
    for receipt in receipts.get("receipts", []):
        receipt_time = datetime.datetime.fromisoformat(receipt["created_at"][:-1])
        hour = receipt_time.hour
        
        if "receipt_type" not in receipt:
            print(f"Skipping receipt due to missing 'receipt_type': {receipt}")
            continue  # Skip this receipt and move to the next one

        #Check if the 'type' key exists and handle accordingly
        #receipt_type = receipt.get("type", "SALE").strip().upper()  # Default to "sale" if 'type' is missing
        #Check if the 'type' key exists and handle accordingly
        receipt_type = receipt["receipt_type"].strip().upper()  # Default to "sale" if 'type' is missing

        total_money = float(receipt["total_money"])

        print(f"Receipt type: {receipt_type}, Total money: {total_money}")
   
        if receipt_type == "REFUND":
            print(f"Applying refund: -{total_money} at hour {hour}")
            hourly_sales[hour]["total_sales"] -= total_money
        elif receipt_type == "SALE":
            hourly_sales[hour]["count"] += 1
            hourly_sales[hour]["total_sales"] += total_money
        else:
            print(f"Unexpected receipt type: {receipt_type}")

    print(f"Final hourly sales data:{hourly_sales}")
    return hourly_sales

def format_sales_data(hourly_sales, date_str):
    formatted_data = []
    
    for hour in range(24):
        sales_data = hourly_sales.get(hour, {"count": 0, "total_sales": 0.0})
        #net_sales = sales_data["total_sales"] - sales_data["total_refunds"]
        formatted_line = f"{STORE_ID}|999999999999|{date_str}|{hour:02d}|{sales_data['count']}|{sales_data['total_sales']:.2f}|0.00|0.00|0.00|0|{sales_data['total_sales']:.2f}|0.00|0.00|0.00|0.00|0.00|0.00|N"
        formatted_data.append(formatted_line)

    return formatted_data

def save_to_file(data_lines, date_str1):
    filename = f"{STORE_ID}_{date_str1}.txt"
    filepath = LOCAL_SAVE_PATH + filename
    
    with open(filepath, "w") as f:
        for line in data_lines:
            f.write(line + "\n")
    
    return filepath

def upload_to_sftp(filepath, filename):
    try:
        # Initialize the SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the SFTP server
        ssh.connect(SFTP_HOST, port=SFTP_PORT, username=SFTP_USERNAME, password=SFTP_PASSWORD)

        sftp = ssh.open_sftp()

        sftp.put(filepath, SFTP_UPLOAD_PATH + filename)
    
        sftp.close()
        ssh.close()

        print(f"Successfully uploaded {filename} to SFTP server.")
    
    except Exception as e:
        print(f"An error occurred during SFTP upload: {e}")

def main():
    # Get current date
    today = datetime.datetime(2024, 8, 22)
    #today = datetime.datetime.now()
    #print(today)
    date_str = today.strftime("%d%m%Y")
    date_str1 = today.strftime("%Y%m%d")
    
    # Define the start and end of the day
    start_time = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Fetch and process sales data
    sales_data = fetch_sales_data(start_time, end_time)
    hourly_sales = process_sales_data(sales_data)
    
    # Format the data
    formatted_data = format_sales_data(hourly_sales, date_str)
    
    # Save to file
    filepath = save_to_file(formatted_data, date_str1)
    
    # Upload to SFTP
    upload_to_sftp(filepath, f"{STORE_ID}_{date_str1}.txt")

if __name__ == "__main__":
    main()
