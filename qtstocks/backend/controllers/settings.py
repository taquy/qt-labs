from flask import jsonify, request, current_app
from models import UserSettings, db
from datetime import datetime, timezone
from functools import wraps
from flask_restx import Resource, fields

def init_settings_routes(app, token_required, settings_ns):
    # Define models for Swagger documentation
    settings_model = settings_ns.model('Settings', {
        'id': fields.Integer(readonly=True, description='Settings ID'),
        'user_id': fields.Integer(readonly=True, description='User ID'),
        'setting_key': fields.String(required=True, description='Setting key'),
        'setting_value': fields.String(description='Setting value'),
        'created_at': fields.DateTime(readonly=True, description='Creation timestamp'),
        'updated_at': fields.DateTime(readonly=True, description='Last update timestamp')
    })

    settings_update_model = settings_ns.model('SettingsUpdate', {
        'setting_value': fields.String(description='Setting value')
    })
    @settings_ns.route('/<string:setting_key>')
    @settings_ns.param('setting_key', 'The setting key')
    class SettingResource(Resource):
        @settings_ns.doc('get_settings', security='Bearer')
        @token_required
        def get(self, current_user, setting_key):
            """Get user settings"""
            try:
                settings = UserSettings.query.filter_by(user_id=current_user.id, setting_key=setting_key).one()
                return settings.setting_value
            except Exception as e:
                print(e)
                return {}
        
        @settings_ns.doc('update_setting', security='Bearer')
        @settings_ns.expect(settings_update_model)
        @settings_ns.marshal_with(settings_model)
        @token_required
        def put(self, current_user, setting_key):
            """Update user settings"""
            if not setting_key:
                settings_ns.abort(400, "Setting key is required")

            # Find existing setting or create new one
            setting = UserSettings.query.filter_by(
                user_id=current_user.id,
                setting_key=setting_key
            ).first()

            if not setting:
                setting = UserSettings(
                    user_id=current_user.id,
                    setting_key=setting_key
                )
                db.session.add(setting)

            # Update setting value
            setting.setting_value = settings_ns.payload['setting_value']
            setting.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            return setting

        @settings_ns.doc('delete_setting', security='Bearer')
        @token_required
        def delete(self, current_user, setting_key):
            """Delete a specific setting"""
            setting = UserSettings.query.filter_by(
                user_id=current_user.id,
                setting_key=setting_key
            ).first()

            if setting:
                db.session.delete(setting)
                db.session.commit()
                return {'message': 'Setting deleted successfully'}
            return {'message': 'Setting not found'}, 404 