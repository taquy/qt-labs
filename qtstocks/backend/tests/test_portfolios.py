import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, request
from controllers.portfolios import init_portfolio_routes
from models import StockPortfolio, Stock, db, User
from flask_restx import Api, Resource, Namespace
from werkzeug.exceptions import NotFound
from datetime import datetime

class TestPortfolios(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Mock the database
        self.db_mock = MagicMock()
        db.session = self.db_mock

        # Create a mock user
        self.mock_user = MagicMock(spec=User)
        self.mock_user.id = 1

        # Create a mock for the token_required decorator
        self.token_required_mock = MagicMock()
        self.token_required_mock.side_effect = lambda f: lambda *args, **kwargs: f(self.mock_user, *args, **kwargs)

        # Initialize the routes
        self.api = Api(self.app)
        self.portfolios_ns = self.api.namespace('portfolios', description='Portfolio operations')
        init_portfolio_routes(self.app, self.token_required_mock, self.portfolios_ns)

        # Mock StockPortfolio and Stock models
        self.mock_portfolio = MagicMock(spec=StockPortfolio)
        self.mock_stock = MagicMock(spec=Stock)

    def tearDown(self):
        patch.stopall()

    def test_list_portfolios(self):
        # Mock the query result
        mock_portfolio = MagicMock(spec=StockPortfolio)
        mock_portfolio.id = 1
        mock_portfolio.user_id = 1
        mock_portfolio.name = "Test Portfolio"
        mock_portfolio.description = "Test Description"
        mock_portfolio.stocks = []
        mock_portfolio.created_at = datetime(2025, 3, 28, 12, 0, 0)
        mock_portfolio.updated_at = datetime(2025, 3, 28, 12, 0, 0)

        # Set up the mock query
        mock_query = MagicMock()
        mock_query.filter_by.return_value.all.return_value = [mock_portfolio]
        self.db_mock.query.return_value = mock_query

        # Make the API call
        response = self.client.get('/portfolios')

        # Assert the response
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['name'], "Test Portfolio")
        self.assertEqual(data[0]['description'], "Test Description")
        self.assertEqual(data[0]['stocks'], [])

        # Verify that the query was called with the correct user_id
        mock_query.filter_by.assert_called_once_with(user_id=self.mock_user.id)

    def test_create_portfolio(self):
        # Prepare the data for creating a new portfolio
        new_portfolio_data = {
            "name": "New Test Portfolio",
            "description": "New Test Description",
            "stock_symbols": ["AAPL", "GOOGL"]
        }

        # Mock the StockPortfolio creation
        mock_portfolio = MagicMock(spec=StockPortfolio)
        mock_portfolio.id = 1
        mock_portfolio.user_id = self.mock_user.id
        mock_portfolio.name = new_portfolio_data["name"]
        mock_portfolio.description = new_portfolio_data["description"]
        mock_portfolio.created_at = datetime(2025, 3, 28, 12, 0, 0)
        mock_portfolio.updated_at = datetime(2025, 3, 28, 12, 0, 0)

        # Mock the stocks
        mock_stocks = []
        for symbol in new_portfolio_data["stock_symbols"]:
            mock_stock = MagicMock(spec=Stock)
            mock_stock.symbol = symbol
            mock_stock.name = f"{symbol} Inc."
            mock_stock.icon = f"https://example.com/{symbol}.png"
            mock_stock.exchange = "NASDAQ"
            mock_stock.market_cap = 1000000.0
            mock_stocks.append(mock_stock)
        mock_portfolio.stocks = mock_stocks

        # Mock StockPortfolio instantiation
        with patch('controllers.portfolios.StockPortfolio') as mock_stock_portfolio:
            mock_stock_portfolio.return_value = mock_portfolio

            # Mock the Stock.query to return mock stocks
            with patch('controllers.portfolios.Stock') as mock_stock:
                mock_stock.query.filter.return_value.all.return_value = mock_stocks

                # Make the API call
                response = self.client.post('/portfolios', json=new_portfolio_data)

        # Assert the response
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], new_portfolio_data['name'])
        self.assertEqual(data['description'], new_portfolio_data['description'])
        self.assertEqual(len(data['stocks']), len(new_portfolio_data['stock_symbols']))

        # Assert that the database operations were called
        self.db_mock.session.add.assert_called_once_with(mock_portfolio)
        self.db_mock.session.commit.assert_called_once()

    def test_get_portfolio(self):
        # Mock the database query for retrieving a specific portfolio
        mock_portfolio = MagicMock(spec=StockPortfolio)
        mock_portfolio.id = 1
        mock_portfolio.user_id = self.mock_user.id
        mock_portfolio.name = "Test Portfolio"
        mock_portfolio.description = "Test Description"
        mock_portfolio.created_at = datetime(2025, 3, 28, 12, 0, 0)
        mock_portfolio.updated_at = datetime(2025, 3, 28, 12, 0, 0)

        # Mock the stocks
        mock_stocks = []
        for symbol in ["AAPL", "GOOGL"]:
            mock_stock = MagicMock(spec=Stock)
            mock_stock.symbol = symbol
            mock_stock.name = f"{symbol} Inc."
            mock_stock.icon = f"https://example.com/{symbol}.png"
            mock_stock.exchange = "NASDAQ"
            mock_stock.market_cap = 1000000.0
            mock_stocks.append(mock_stock)
        mock_portfolio.stocks = mock_stocks

        self.db_mock.query.return_value.get_or_404.return_value = mock_portfolio

        # Make the API call
        response = self.client.get('/portfolios/1')

        # Assert the response
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], "Test Portfolio")
        self.assertEqual(data['description'], "Test Description")
        self.assertEqual(len(data['stocks']), 2)
        self.assertEqual(data['stocks'][0]['symbol'], "AAPL")
        self.assertEqual(data['stocks'][1]['symbol'], "GOOGL")

        # Test case for non-existent portfolio
        self.db_mock.query.return_value.get_or_404.side_effect = NotFound()
        response = self.client.get('/portfolios/999')
        self.assertEqual(response.status_code, 404)

        # Reset the side effect
        self.db_mock.query.return_value.get_or_404.side_effect = None

        # Test case for portfolio belonging to another user
        mock_portfolio.user_id = self.mock_user.id + 1
        response = self.client.get('/portfolios/1')
        self.assertEqual(response.status_code, 403)

    def test_update_portfolio(self):
        # Mock the database query for retrieving the portfolio to be updated
        mock_portfolio = MagicMock(spec=StockPortfolio)
        mock_portfolio.id = 1
        mock_portfolio.user_id = self.mock_user.id
        mock_portfolio.name = "Old Portfolio Name"
        mock_portfolio.description = "Old Description"
        mock_portfolio.created_at = datetime(2025, 3, 28, 12, 0, 0)
        mock_portfolio.updated_at = datetime(2025, 3, 28, 12, 0, 0)

        # Mock initial stock
        mock_stock = MagicMock(spec=Stock)
        mock_stock.symbol = "AAPL"
        mock_stock.name = "Apple Inc."
        mock_stock.icon = "https://example.com/AAPL.png"
        mock_stock.exchange = "NASDAQ"
        mock_stock.market_cap = 1000000.0
        mock_portfolio.stocks = [mock_stock]

        self.db_mock.query.return_value.get_or_404.return_value = mock_portfolio

        # Prepare the data for updating the portfolio
        update_data = {
            "name": "Updated Portfolio Name",
            "description": "Updated Description",
            "stock_symbols": ["AAPL", "GOOGL"]
        }

        # Mock the new stocks
        mock_stocks = []
        for symbol in update_data["stock_symbols"]:
            mock_stock = MagicMock(spec=Stock)
            mock_stock.symbol = symbol
            mock_stock.name = f"{symbol} Inc."
            mock_stock.icon = f"https://example.com/{symbol}.png"
            mock_stock.exchange = "NASDAQ"
            mock_stock.market_cap = 1000000.0
            mock_stocks.append(mock_stock)

        with patch('controllers.portfolios.Stock') as mock_stock:
            mock_stock.query.filter.return_value.all.return_value = mock_stocks

            # Make the API call
            response = self.client.put('/portfolios/1', json=update_data)

        # Assert the response
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], update_data['name'])
        self.assertEqual(data['description'], update_data['description'])
        self.assertEqual(len(data['stocks']), len(update_data['stock_symbols']))

        # Assert that the database operations were called
        self.db_mock.session.commit.assert_called_once()

        # Test case for non-existent portfolio
        self.db_mock.query.return_value.get_or_404.side_effect = NotFound()
        response = self.client.put('/portfolios/999', json=update_data)
        self.assertEqual(response.status_code, 404)

        # Reset the side effect
        self.db_mock.query.return_value.get_or_404.side_effect = None

        # Test case for portfolio belonging to another user
        mock_portfolio.user_id = self.mock_user.id + 1
        response = self.client.put('/portfolios/1', json=update_data)
        self.assertEqual(response.status_code, 403)

        # Reset user_id
        mock_portfolio.user_id = self.mock_user.id

        # Test case for duplicate portfolio name
        with patch('controllers.portfolios.StockPortfolio') as mock_stock_portfolio:
            mock_stock_portfolio.query.filter_by.return_value.first.return_value = MagicMock()
            response = self.client.put('/portfolios/1', json=update_data)
            self.assertEqual(response.status_code, 400)

    def test_delete_portfolio(self):
        # Mock the database query for retrieving the portfolio to be deleted
        mock_portfolio = MagicMock(spec=StockPortfolio)
        mock_portfolio.id = 1
        mock_portfolio.user_id = self.mock_user.id
        mock_portfolio.name = "Portfolio to Delete"
        mock_portfolio.description = "This portfolio will be deleted"
        mock_portfolio.created_at = datetime(2025, 3, 28, 12, 0, 0)
        mock_portfolio.updated_at = datetime(2025, 3, 28, 12, 0, 0)

        # Mock stock
        mock_stock = MagicMock(spec=Stock)
        mock_stock.symbol = "AAPL"
        mock_stock.name = "Apple Inc."
        mock_stock.icon = "https://example.com/AAPL.png"
        mock_stock.exchange = "NASDAQ"
        mock_stock.market_cap = 1000000.0
        mock_portfolio.stocks = [mock_stock]

        self.db_mock.query.return_value.get_or_404.return_value = mock_portfolio

        # Make the API call
        response = self.client.delete('/portfolios/1')

        # Assert the response
        self.assertEqual(response.status_code, 204)

        # Assert that the database operations were called
        self.db_mock.session.delete.assert_called_once_with(mock_portfolio)
        self.db_mock.session.commit.assert_called_once()

        # Test case for non-existent portfolio
        self.db_mock.query.return_value.get_or_404.side_effect = NotFound()
        response = self.client.delete('/portfolios/999')
        self.assertEqual(response.status_code, 404)

        # Reset the side effect
        self.db_mock.query.return_value.get_or_404.side_effect = None

        # Test case for portfolio belonging to another user
        mock_portfolio.user_id = self.mock_user.id + 1
        response = self.client.delete('/portfolios/1')
        self.assertEqual(response.status_code, 403)

        # Reset user_id
        mock_portfolio.user_id = self.mock_user.id

if __name__ == '__main__':
    unittest.main()
