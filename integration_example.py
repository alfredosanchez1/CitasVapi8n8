"""
Ejemplo de cómo integrar el módulo de Vapi con tu API existente en Render
"""

# Si usas Flask
from flask import Flask, request, jsonify
from vapi_integration import process_vapi_webhook, create_medical_call

app = Flask(__name__)

# Endpoint para webhook de Vapi
@app.route('/vapi-webhook', methods=['POST'])
def vapi_webhook():
    """Endpoint para recibir webhooks de Vapi"""
    try:
        webhook_data = request.get_json()
        result = process_vapi_webhook(webhook_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Endpoint para crear llamadas
@app.route('/create-call', methods=['POST'])
def create_call():
    """Crear una llamada médica"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        patient_info = data.get('patient_info', {})
        
        if not phone_number:
            return jsonify({"error": "phone_number es requerido"}), 400
        
        result = create_medical_call(phone_number, patient_info)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Si usas FastAPI
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from vapi_integration import process_vapi_webhook, create_medical_call

app = FastAPI()

class CallRequest(BaseModel):
    phone_number: str
    patient_info: dict = {}

@app.post("/vapi-webhook")
async def vapi_webhook(request: Request):
    webhook_data = await request.json()
    return process_vapi_webhook(webhook_data)

@app.post("/create-call")
async def create_call(call_request: CallRequest):
    result = create_medical_call(call_request.phone_number, call_request.patient_info)
    return result
"""

# Si usas Django
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from vapi_integration import process_vapi_webhook, create_medical_call

@csrf_exempt
@require_http_methods(["POST"])
def vapi_webhook(request):
    webhook_data = json.loads(request.body)
    result = process_vapi_webhook(webhook_data)
    return JsonResponse(result)

@csrf_exempt
@require_http_methods(["POST"])
def create_call(request):
    data = json.loads(request.body)
    phone_number = data.get('phone_number')
    patient_info = data.get('patient_info', {})
    
    if not phone_number:
        return JsonResponse({"error": "phone_number es requerido"}, status=400)
    
    result = create_medical_call(phone_number, patient_info)
    return JsonResponse(result)
"""

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000) 