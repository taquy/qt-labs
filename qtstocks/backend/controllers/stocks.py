from flask import jsonify, request, Response
from datetime import datetime, timezone
import io
import csv
from models import Stock, StockStats, user_stock_stats
from extensions import db
from services.get_stock_lists import get_stock_list
from services.get_stock_data import process_stock_list

def init_stock_routes(app, token_required):
    @app.route('/api/stocks')
    @token_required
    def get_stocks(current_user):
        try:
            stocks = Stock.query.all()
            return jsonify({
                'stocks': [
                    {
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'last_updated': stock.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    for stock in stocks
                ]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stocks_with_stats')
    @token_required
    def get_stocks_with_stats(current_user):
        try:
            # Query stocks that have stats
            stocks_with_stats = db.session.query(Stock).join(StockStats).join(user_stock_stats).filter(user_stock_stats.c.user_id == current_user.id).all()
            return jsonify({
                'stocks': [
                    {
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'last_updated': stock.stats.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
                        'price': stock.stats.price,
                        'market_cap': stock.stats.market_cap,
                        'eps': stock.stats.eps,
                        'pe': stock.stats.pe,
                        'pb': stock.stats.pb
                    }
                    for stock in stocks_with_stats
                ]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/download_stock_list', methods=['POST'])
    @token_required
    def download_stock_list(current_user):
        try:
            stocks = get_stock_list()
            
            for stock_data in stocks:
                existing_stock = Stock.query.filter_by(symbol=stock_data['Symbol']).first()
                if existing_stock:
                    continue
                stock = Stock(
                    symbol=stock_data['Symbol'],
                    name=stock_data['Name'],
                    last_updated=datetime.now(timezone.utc)
                )
                db.session.add(stock)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Successfully downloaded {len(stocks)} stocks'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/fetch_stock_data', methods=['POST'])
    @token_required
    def fetch_stock_data(current_user):
        try:
            data = request.get_json()
            if not data or 'symbols' not in data:
                return jsonify({'error': 'No stock symbols provided'}), 400
                
            symbols = data['symbols']
            if not symbols:
                return jsonify({'error': 'Empty stock symbols list'}), 400
            
            fetching_latest = data.get('loadLatestData', False)
            
            # Verify all symbols exist in database
            for symbol in symbols:
                stock = Stock.query.filter_by(symbol=symbol).first()
                if not stock:
                    return jsonify({'error': f'Stock {symbol} not found in database'}), 404
                
            if fetching_latest:
                new_symbols = symbols
            else:
                # reuse existing stock stats if already available in stock_stats table
                new_symbols = []
                for symbol in symbols:
                    stock_stat = StockStats.query.filter_by(symbol=symbol).first()
                    if stock_stat:
                        if stock_stat not in current_user.stock_stats:
                            current_user.stock_stats.append(stock_stat)
                    else:
                        new_symbols.append(symbol)
                db.session.commit()
            
            # scrape data for any new symbols
            if len(new_symbols) > 0:
                process_stock_list(new_symbols, current_user)
            
            return jsonify({
                'success': True,
                'message': f'Successfully fetched data for {len(new_symbols)} stocks {", ".join(new_symbols)}'
            })
            
        except Exception as e:
            print(f"Error in fetch_stock_data: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/remove_stock_stats', methods=['POST'])
    @token_required
    def remove_stock_stats(current_user):
        try:
            data = request.get_json()
            if not data or 'symbols' not in data:
                return jsonify({'error': 'No stock symbols provided'}), 400
                
            symbols = data['symbols']
            if not symbols:
                return jsonify({'error': 'Empty stock symbols list'}), 400
            
            # Delete stats for each symbol
            for symbol in symbols:
                stats = StockStats.query.filter_by(symbol=symbol).first()
                if stats:
                    db.session.delete(stats)
            
            # Delete user_stock_stats for each symbol
            for symbol in symbols:
                user_stock_stat = db.session.query(user_stock_stats).filter_by(stock_symbol=symbol, user_id=current_user.id).first()
                if user_stock_stat:
                    db.session.delete(user_stock_stat)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Successfully removed stats for {len(symbols)} stocks'
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"Error in remove_stock_stats: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/export_csv')
    @token_required
    def export_stocks(current_user):
        try:
            # Create CSV data
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Symbol', 'Name', 'Price', 'Market Cap', 'EPS', 'P/E', 'P/B', 'Last Updated'])
            
            stocks_with_stats = db.session.query(Stock)\
                .join(StockStats)\
                .join(user_stock_stats)\
                .filter(user_stock_stats.c.user_id == current_user.id)\
                .all()
                        
            for stock in stocks_with_stats:
                writer.writerow([
                    stock.symbol,
                    stock.name,
                    stock.stats.price,
                    stock.stats.market_cap,
                    stock.stats.eps,
                    stock.stats.pe,
                    stock.stats.pb,
                    stock.stats.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            # Create response
            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=stocks_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}.csv'
                }
            )
            
        except Exception as e:
            print(f"Error exporting stocks: {str(e)}")
            return {'error': str(e)}, 500 
    