from flask import jsonify, request
from datetime import datetime, UTC
from models import UserSettings
from extensions import db

def init_settings_routes(app, token_required):
    @app.route('/api/settings', methods=['GET'])
    @token_required
    def get_settings(current_user):
        try:
            # Get all settings for the current user
            settings = UserSettings.query.filter_by(user_id=current_user.id).all()
            return jsonify({
                'settings': {setting.setting_key: setting.setting_value for setting in settings}
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/settings/<setting_key>', methods=['PUT'])
    @token_required
    def update_setting(current_user, setting_key):
        try:
            data = request.get_json()
            if not data or 'value' not in data:
                return jsonify({'error': 'No data received'}), 400

            # Find existing setting or create new one
            setting = UserSettings.query.filter_by(
                user_id=current_user.id,
                setting_key=setting_key
            ).first()

            if setting:
                setting.setting_value = data['value']
                setting.updated_at = datetime.now(UTC)
            else:
                setting = UserSettings(
                    user_id=current_user.id,
                    setting_key=setting_key,
                    setting_value=data['value']
                )
                db.session.add(setting)

            db.session.commit()
            return jsonify(setting.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/settings/<setting_key>', methods=['DELETE'])
    @token_required
    def delete_setting(current_user, setting_key):
        try:
            setting = UserSettings.query.filter_by(
                user_id=current_user.id,
                setting_key=setting_key
            ).first()

            if setting:
                db.session.delete(setting)
                db.session.commit()
                return jsonify({'message': 'Setting deleted successfully'})
            return jsonify({'message': 'Setting not found'}), 404
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500 