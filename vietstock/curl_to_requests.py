import requests
import json

def get_finance_info(code='FPT', page=1, page_size=4):
    url = 'https://finance.vietstock.vn/data/financeinfo'
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://finance.vietstock.vn',
        'Referer': 'https://finance.vietstock.vn/',
    }
    
    # Cookies
    cookies = {
        '__RequestVerificationToken': 'IaEETWWQbgd6Q3HWs5MlztmjfPkpNVNnhejl7oEy4ZMQKktbMVzpFTYUop7uF-GGYl76vfZEKX1QEiBZLKUoMZM2mDXXlyPdpLWuv3d7xTE1'
    }
    
    # Request data
    data = {
        'Code': code,
        'Page': page,
        'PageSize': page_size,
        'ReportTermType': 1,
        'ReportType': 'BCTQ',
        'Unit': 1000000,
        '__RequestVerificationToken': 'lApy7ZaGHHNOxcYmKc2fHgw2kyXB4ncN0mavdCKEaHpy6fIQMBgZTOWcTr_L0ArdxWQHzfWK2UqSTkUCiea7B6_yXSDW1LNq1eF2ZioDtug1'
    }
    
    # Make the POST request
    response = requests.post(url, headers=headers, cookies=cookies, data=data)
    
    try:
        if response.status_code == 200:
            data = response.json()
            # Extract P/E and EPS from the response
            result = {
                'code': code,
                'status': 'success',
                'data': data,
                'pe_ratio': None,
                'eps': None
            }
            
            if isinstance(data, list) and len(data) > 0:
                for item in data:
                    if 'PE' in item:
                        result['pe_ratio'] = item['PE']
                    if 'EPS' in item:
                        result['eps'] = item['EPS']
            
            return result
        else:
            return {
                'code': code,
                'status': 'error',
                'message': f"HTTP Error: {response.status_code}",
                'pe_ratio': None,
                'eps': None
            }
    except json.JSONDecodeError:
        return {
            'code': code,
            'status': 'error',
            'message': "Failed to parse JSON response",
            'pe_ratio': None,
            'eps': None
        }
    except Exception as e:
        return {
            'code': code,
            'status': 'error',
            'message': str(e),
            'pe_ratio': None,
            'eps': None
        }

if __name__ == "__main__":
    # Example usage
    result = get_finance_info()
    print(result) 