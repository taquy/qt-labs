from curl_to_requests import get_finance_info

def display_stock_info(result):
    print(f"Stock Code: {result['code']}")
    print(f"Status: {result['status']}")
    
    if result['status'] == 'success':
        print(f"P/E Ratio: {result['pe_ratio']}")
        print(f"EPS: {result['eps']}")
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")
    print("-" * 40)

def main():
    # Example 1: Get data for FPT with default parameters
    print("Getting data for FPT:")
    result = get_finance_info()
    display_stock_info(result)

    # Example 2: Get data for VNM with custom parameters
    print("Getting data for VNM:")
    result = get_finance_info(code='VNM', page=1, page_size=10)
    display_stock_info(result)

    # Example 3: Get data for HPG
    print("Getting data for HPG:")
    result = get_finance_info(code='HPG', page=1, page_size=4)
    display_stock_info(result)

if __name__ == "__main__":
    main() 