    BASE_URL = "https://finance.vietstock.vn/"
    LOGIN_URL = urljoin(BASE_URL, "Account/Login")
    # Updated URL patterns based on actual website structure
    COMPANY_DATA_URL = "{}/company-info"  # Will be formatted with symbol
    FINANCIAL_INDICATORS_URL = "{}/financial-indicators"  # Will be formatted with symbol
            logger.warning("No credentials provided. Some features may not work.")
            
        self.session = requests.Session()
        # Updated headers to better match browser behavior
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': self.BASE_URL.rstrip('/'),
            'Referer': self.BASE_URL,
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'Cache-Control': 'max-age=0',
        })
        # Track request retry counts
        self.retry_counts = {}
        if not self.authenticated:
            return self.login()
        return True
        
    def _make_request_with_retry(self, method, url, max_retries=3, retry_delay=2, **kwargs):
        """
        Make HTTP request with retry mechanism for failed requests
        
        Args:
            method: HTTP method ('get' or 'post')
            url: Request URL
            max_retries: Maximum number of retries
            retry_delay: Base delay between retries (will be increased with backoff)
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object if successful, None if all retries failed
        """
        # Track retry counts for this URL
        if url not in self.retry_counts:
            self.retry_counts[url] = 0
            
        # Get the appropriate request method from session
        request_method = getattr(self.session, method.lower())
        
        for attempt in range(max_retries):
            try:
                # Add a slight delay to avoid hitting rate limits
                if attempt > 0:
                    # Exponential backoff with jitter
                    delay = retry_delay * (2 ** attempt) + random.uniform(0.1, 1.0)
                    logger.info(f"Retry attempt {attempt+1}/{max_retries}. Waiting {delay:.2f} seconds...")
                    time.sleep(delay)
                
                # Make the request
                response = request_method(url, **kwargs)
                
                # Check for common error status codes
                if response.status_code in [429, 503, 502, 500]:
                    logger.warning(f"Received status code {response.status_code}. Will retry.")
                    self.retry_counts[url] += 1
                    continue
                    
                # If successful, reset retry counter and return response
                if response.status_code == 200:
                    self.retry_counts[url] = 0
                    return response
                    
                # If we got a different error code, log it but still return the response
                logger.warning(f"Request to {url} returned status code {response.status_code}")
                return response
                
            except (requests.ConnectionError, requests.Timeout) as e:
                logger.warning(f"Request failed (attempt {attempt+1}/{max_retries}): {str(e)}")
                self.retry_counts[url] += 1
                
                # If this is the last attempt, re-raise the exception
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} retry attempts failed for {url}")
                    return None
                    
        return None
    def get_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get stock data for a given symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'VCB' for Vietcombank)
            
        Returns:
            dict: Stock data if successful, None otherwise
        """
        if not self._ensure_authenticated():
            logger.error("Cannot get stock data: Not authenticated")
            return None
            
        try:
            # Format the URL with the symbol
            symbol = symbol.upper()
            url = urljoin(self.BASE_URL, self.COMPANY_DATA_URL.format(symbol))
            
            # Prepare headers for company information request
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Referer': f"{self.BASE_URL}{symbol}",
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
            }
            
            # Add CSRF token if available
            if self.csrf_token:
                headers['X-CSRF-Token'] = self.csrf_token
            
            # Use the retry mechanism for the request
            response = self._make_request_with_retry(
                'get',
                url,
                headers=headers,
                timeout=15
            )
            
            # Return None if all retries failed
            if response is None:
                logger.error(f"Failed to get stock data for {symbol} after multiple retries")
                return None
    def get_financial_indicators(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get financial indicators (like EPS, P/E, P/B) for a given stock symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'VCB' for Vietcombank)
            
        Returns:
            dict: Financial indicators data if successful, None otherwise
        """
        if not self._ensure_authenticated():
            logger.error("Cannot get financial indicators: Not authenticated")
            return None
            
        try:
            # Format the URL with the symbol
            symbol = symbol.upper()
            url = urljoin(self.BASE_URL, self.FINANCIAL_INDICATORS_URL.format(symbol))
            
            # Updated headers to match website's actual requests
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Referer': f"{self.BASE_URL}{symbol}",
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
            }
            
            if self.csrf_token:
                headers['X-CSRF-Token'] = self.csrf_token
            
            # Use the retry mechanism for the request
            response = self._make_request_with_retry(
                'get',
                url,
                headers=headers,
                timeout=15
            )
            
            
