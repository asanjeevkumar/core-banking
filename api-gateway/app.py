from flask import Flask, request, jsonify, Response

import requests

@app.route('/', defaults={'path': ''})

# Simple in-memory service registry (for demonstration)
service_registry = {
    'user-service': 'http://localhost:5001',
    'loan-service': 'http://localhost:5002',
    'collection-service': 'http://localhost:5003',
    'reporting-service': 'http://localhost:5004'
}

app = Flask(__name__)
@app.route('/<path:path>')
def catch_all(path):
    # Basic path-based routing
    target_url = None
    if path.startswith('users'):
        target_url = service_registry.get('user-service')
    elif path.startswith('loans'):
        service_location = service_registry.get('loan-service', 'Unknown Location')
        target_url = f"{service_location}/{path}"
    elif path.startswith('repayments'):
        target_url = service_registry.get('collection-service')
    elif path.startswith('reports'):
        target_url = service_registry.get('reporting-service')
    
    if target_url:
        try:
            response = requests.request(
                method=request.method,
                url=f"{target_url}/{path}",
                headers={key: value for (key, value) in request.headers if key != 'Host'},
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=False)

            # Exclude 'Transfer-Encoding' and 'Content-Encoding' headers
            excluded_headers = ['transfer-encoding', 'content-encoding']
            headers = [(name, value) for (name, value) in response.raw.headers.items() if name.lower() not in excluded_headers]

            return Response(response.content, response.status_code, headers)

        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Error forwarding request to service: {e}'}), 500
    else:
        return jsonify({'message': f'No service configured for path: /{path}'}), 404


    # Basic path-based routing - Old logic
    # if path.startswith('users'):
    #     service = 'User Service'
    #     # TODO: Forward request to User Service
    # elif path.startswith('loans'):
    #     service = 'Loan Service'
    #     # TODO: Forward request to Loan Service
    #     service_location = service_registry.get('loan-service', 'Unknown Location')
    # elif path.startswith('repayments'):
    #     service = 'Repayment Service'
        # TODO: Forward request to Repayment Service
        service_location = service_registry.get('repayment-service', 'Unknown Location')
    else:
        service = 'Unknown Service'
        service_location = 'N/A'
    return jsonify({'message': f'Routing request for /{path} to {service} at {service_location}'}), 200
# End of old logic
if __name__ == '__main__':
    app.run(debug=True, port=5000)
