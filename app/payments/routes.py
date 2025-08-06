from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User
from .. import db
import stripe
import os
import json

payments_bp = Blueprint('payments', __name__)

# Configurar Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_placeholder')

# Planes disponibles
PLANS = {
    'weekly': {
        'name': 'Plan Semanal',
        'price': 9.99,
        'stripe_price_id': 'price_weekly',
        'features': ['5 videos por semana', 'Clips ilimitados', 'Soporte prioritario']
    },
    'monthly': {
        'name': 'Plan Mensual',
        'price': 29.99,
        'stripe_price_id': 'price_monthly',
        'features': ['Videos ilimitados', 'Clips ilimitados', 'Soporte prioritario', 'Subtítulos personalizados']
    },
    'yearly': {
        'name': 'Plan Anual',
        'price': 299.99,
        'stripe_price_id': 'price_yearly',
        'features': ['Todo del plan mensual', '50% descuento', 'Acceso anticipado a nuevas funciones']
    },
    'lifetime': {
        'name': 'Plan Vitalicio',
        'price': 999.99,
        'stripe_price_id': 'price_lifetime',
        'features': ['Acceso de por vida', 'Todas las funciones', 'Soporte VIP', 'Actualizaciones gratuitas']
    }
}

@payments_bp.route('/plans', methods=['GET'])
def get_plans():
    """Obtener planes disponibles"""
    try:
        return jsonify({
            'plans': PLANS,
            'currency': 'USD'
        }), 200
    except Exception as e:
        print(f"Error al obtener planes: {str(e)}")
        return jsonify({'error': 'Error al obtener planes'}), 500

@payments_bp.route('/create-checkout-session', methods=['POST'])
@jwt_required()
def create_checkout_session():
    """Crear sesión de checkout de Stripe"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        plan_id = data.get('plan_id')
        if not plan_id or plan_id not in PLANS:
            return jsonify({'error': 'Plan inválido'}), 400
        
        plan = PLANS[plan_id]
        
        # Obtener usuario
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Crear sesión de checkout
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': plan['name'],
                        'description': f"Plan {plan['name']} - AI Net"
                    },
                    'unit_amount': int(plan['price'] * 100),  # Stripe usa centavos
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{request.headers.get('Origin', 'https://tu-frontend.com')}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.headers.get('Origin', 'https://tu-frontend.com')}/cancel",
            metadata={
                'user_id': user_id,
                'plan_id': plan_id
            }
        )
        
        return jsonify({
            'session_id': checkout_session.id,
            'checkout_url': checkout_session.url
        }), 200
        
    except Exception as e:
        print(f"Error al crear sesión de checkout: {str(e)}")
        return jsonify({'error': 'Error al crear sesión de pago'}), 500

@payments_bp.route('/webhook', methods=['POST'])
def webhook():
    """Webhook de Stripe para procesar pagos"""
    try:
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')
        
        # Verificar webhook (en producción deberías verificar la firma)
        # event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        
        # Por ahora procesamos sin verificación
        event = stripe.Event.construct_from(json.loads(payload), sig_header)
        
        if event.type == 'checkout.session.completed':
            session = event.data.object
            
            # Actualizar plan del usuario
            user_id = session.metadata.get('user_id')
            plan_id = session.metadata.get('plan_id')
            
            if user_id and plan_id:
                user = User.query.get(user_id)
                if user:
                    user.plan = plan_id
                    db.session.commit()
                    
                    print(f"Usuario {user.email} actualizado al plan {plan_id}")
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f"Error en webhook: {str(e)}")
        return jsonify({'error': 'Error en webhook'}), 400

@payments_bp.route('/subscription-status', methods=['GET'])
@jwt_required()
def get_subscription_status():
    """Obtener estado de la suscripción del usuario"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        current_plan = PLANS.get(user.plan, PLANS['free'])
        
        return jsonify({
            'current_plan': user.plan,
            'plan_details': current_plan,
            'features': current_plan.get('features', [])
        }), 200
        
    except Exception as e:
        print(f"Error al obtener estado de suscripción: {str(e)}")
        return jsonify({'error': 'Error al obtener estado de suscripción'}), 500

@payments_bp.route('/cancel-subscription', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancelar suscripción (volver a plan gratuito)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Volver a plan gratuito
        user.plan = 'free'
        db.session.commit()
        
        return jsonify({
            'message': 'Suscripción cancelada exitosamente',
            'new_plan': 'free'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al cancelar suscripción: {str(e)}")
        return jsonify({'error': 'Error al cancelar suscripción'}), 500 