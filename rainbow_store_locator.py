
import pymysql
from parsel import Selector
import re
import requests

# Database Connection
try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="actowiz",
        database="use_db"
    )
    cursor = conn.cursor()
except pymysql.MySQLError as e:
    print(f"Error connecting to database: {e}")
    exit()

# Cookie and header setup (you can keep this as is)
cookies = {
    'ARRAffinity': 'b4fef3836a2d74e910ebb018f67082e96c3d30fc5812393bdc8708a4858891b6',
    'ARRAffinitySameSite': 'b4fef3836a2d74e910ebb018f67082e96c3d30fc5812393bdc8708a4858891b6',
    '_ga': 'GA1.1.1043974752.1732180169',
    'FPID': 'FPID2.2.b0%2F%2FKkrDuhdKp%2FUvXIJPKH3yRSFEJHIOjrGaZxDMYqM%3D.1732180169',
    'FPLC': 'C3lLDiPSdYSWBjGMKPFsWAQCduE6c34tYQoAL8iAk9G8PlkIH87ylcX9H5edD6yNFshpkdMMrKTla1ZSZDPDD91lxIUmAWC%2Bivzd0X5twa%2FBWNxzDcATfRcZ8xcIzw%3D%3D',
    '_ga_8JYLGEF9DT': 'GS1.1.1732180169.1.1.1732180292.0.0.1734211871',
    '_ga_DQ3HWRZ4R8': 'GS1.1.1732180169.1.1.1732180292.0.0.119380646',
}
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    # 'cookie': 'ARRAffinity=b4fef3836a2d74e910ebb018f67082e96c3d30fc5812393bdc8708a4858891b6; ARRAffinitySameSite=b4fef3836a2d74e910ebb018f67082e96c3d30fc5812393bdc8708a4858891b6; _ga=GA1.1.1043974752.1732180169; FPID=FPID2.2.b0%2F%2FKkrDuhdKp%2FUvXIJPKH3yRSFEJHIOjrGaZxDMYqM%3D.1732180169; FPLC=C3lLDiPSdYSWBjGMKPFsWAQCduE6c34tYQoAL8iAk9G8PlkIH87ylcX9H5edD6yNFshpkdMMrKTla1ZSZDPDD91lxIUmAWC%2Bivzd0X5twa%2FBWNxzDcATfRcZ8xcIzw%3D%3D; _ga_8JYLGEF9DT=GS1.1.1732180169.1.1.1732180292.0.0.1734211871; _ga_DQ3HWRZ4R8=GS1.1.1732180169.1.1.1732180292.0.0.119380646',
    'priority': 'u=0, i',
    'referer': 'https://www.google.com/',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

def extract_schedule(html: str) -> str:
    # Define a regex pattern to capture days and their corresponding times
    pattern = r'<td class="table-day">(\w+)</td>\s*<td class="table-time ">\s*([\d:APM\- ]+)'
    matches = re.findall(pattern, html)

    # Format the schedule as "DAY:TIME | DAY:TIME ..."
    formatted_schedule = [f"{day}:{time.strip()}" for day, time in matches]
    return " | ".join(formatted_schedule)


# Function to insert data into the database
def insert_store_data(details):
    # SQL Insert query
    insert_query = '''
    INSERT INTO Rainbow_store_locator (
        store_name, store_name_xpath, store_name_html,
        store_url, store_url_xpath, store_url_html,
        store_number, store_number_xpath, store_number_html,
        store_address, store_address_xpath, store_address_html,
        store_contact, store_contact_xpath, store_contact_html,
        store_time, store_time_xpath, store_time_html
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cursor.execute(insert_query, (
        details["store_name"], details["store_name_xpath"], details["store_name_html"],
        details["store_url"], details["store_url_xpath"], details["store_url_html"],
        details["store_number"], details["store_number_xpath"], details["store_number_html"],
        details["store_address"], details["store_address_xpath"], details["store_address_html"],
        details["store_contact"], details["store_contact_xpath"], details["store_contact_html"],
        details["store_time"], details["store_time_xpath"], details["store_time_html"]
    ))

    # Commit the transaction
    conn.commit()


response = requests.get('https://stores.rainbowshops.com/', cookies=cookies, headers=headers)
parsed_data = Selector(response.text)
urls = parsed_data.xpath('//div[@class="state"]')

for url in urls:
    state_url = 'https://stores.rainbowshops.com/' + url.xpath('.//a//@href').get()
    response2 = requests.get(state_url, headers=headers, cookies=cookies)
    parsed_data2 = Selector(response2.text)
    boxes = parsed_data2.xpath('//div[@class="state-infobox"]')
    for box in boxes:

        store_name = box.xpath('.//div[@class="state-infobox-title"]//a//text()').get()
        store_name_xpath = '//div[@class="state-infobox-title"]//a//text()'
        store_name_html = box.xpath('.//div[@class="state-infobox-title"]//a').getall()

        store_url = 'https://stores.rainbowshops.com/' + box.xpath('.//div[@class="state-infobox-title"]//a//@href').get()
        store_url_xpath = '//div[@class="state-infobox-title"]//a//@href'
        store_url_html = box.xpath('.//div[@class="state-infobox-title"]//a').getall()

        store_number = box.xpath('.//div[@class="state-infobox-address"][1]//text()').get()
        store_number2 = re.sub(r'\s+', ' ', store_number).strip().split()[-1]
        store_number_xpath = '//div[@class="state-infobox-address"][1]//text()'
        store_number_html = box.xpath('//div[@class="state-infobox-address"][1]').get()

        store_address = box.xpath('.//div[@class="state-infobox-address"][2]//text()').getall()
        input_str = ' '.join(store_address)
        store_address2 = re.sub(r'\s+', ' ', input_str).strip()
        store_address_xpath = './/div[@class="state-infobox-address"][2]//text()'
        store_address_html = box.xpath('.//div[@class="state-infobox-address"][2]').getall()

        store_contact = box.xpath('.//div[@class="state-infobox-phone"]//a//text()').get()
        store_contact_xpath = './/div[@class="state-infobox-phone"]//a//text()'
        store_contact_html = box.xpath('.//div[@class="state-infobox-phone"]//a').getall()

        response3 = requests.get(store_url, headers=headers, cookies=cookies)
        parsed_data3 = Selector(response3.text)
        store_time = parsed_data3.xpath(
            '//div[@id="locdetails"]//div[@class="table-responsive"]//table[@class="table table-borderless table-sm loc-hours-table"]//tr/td').getall()[:14]

        store_time = ' '.join(store_time)
        weak_store_time = extract_schedule(store_time)
        store_time_xpath = '//div[@id="locdetails"]//div[@class="table-responsive"]//table[@class="table table-borderless table-sm loc-hours-table"]//tr/td'
        store_time_html = store_time

        # Prepare the details dictionary for insertion
        details = {
            "store_name": store_name,
            "store_name_xpath": store_name_xpath,
            "store_name_html": store_name_html,

            "store_url": store_url,
            "store_url_xpath": store_url_xpath,
            "store_url_html": store_url_html,

            "store_number": store_number2,
            "store_number_xpath": store_number_xpath,
            "store_number_html": store_number_html,

            "store_address": store_address2,
            "store_address_xpath": store_address_xpath,
            "store_address_html": store_address_html,

            "store_contact": store_contact,
            "store_contact_xpath": store_contact_xpath,
            "store_contact_html": store_contact_html,

            "store_time": weak_store_time,
            "store_time_xpath": store_time_xpath,
            "store_time_html": store_time_html
        }

        # Insert the store data into the database
        insert_store_data(details)

# Close the connection
conn.close()
