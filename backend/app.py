from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime
import csv
from io import TextIOWrapper
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Flask setup
app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

# DB setup
db_path = os.getenv("DATABASE", "sqlite.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///../instance/{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
# DB model
class Voucher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    expiry = db.Column(db.Date, nullable=False)

# Routes
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/admin')
def admin_panel():
    return send_from_directory(app.static_folder, 'admin.html')

@app.route('/check-voucher', methods=['POST'])
def check_voucher():
    data = request.get_json()
    code = data.get('code', '').strip()

    voucher = Voucher.query.filter_by(code=code).first()
    if voucher and voucher.expiry >= datetime.today().date():
        return jsonify({
            "valid": True,
            "type": voucher.type,
            "expires": voucher.expiry.strftime('%Y-%m-%d')
        })
    return jsonify({"valid": False})

@app.route('/add-voucher', methods=['POST'])
def add_voucher():
    data = request.get_json()
    code = data.get('code')
    type_ = data.get('type')
    expiry = datetime.strptime(data.get('expiry'), '%Y-%m-%d').date()

    if not Voucher.query.filter_by(code=code).first():
        new_voucher = Voucher(code=code, type=type_, expiry=expiry)
        db.session.add(new_voucher)
        db.session.commit()

    return jsonify({"status": "ok"})

@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    stream = TextIOWrapper(file.stream)
    reader = csv.DictReader(stream)

    for row in reader:
        code = row['code'].strip()
        type_ = row['type'].strip()
        expiry = datetime.strptime(row['expiry'].strip(), '%Y-%m-%d').date()
        if not Voucher.query.filter_by(code=code).first():
            db.session.add(Voucher(code=code, type=type_, expiry=expiry))

    db.session.commit()
    return jsonify({'status': 'uploaded'})

@app.route('/vouchers')
def get_vouchers():
    vouchers = Voucher.query.all()
    return jsonify([{
        'code': v.code,
        'type': v.type,
        'expiry': v.expiry.strftime('%Y-%m-%d')
    } for v in vouchers])

# Entry point for local or Render
if __name__ == '__main__':
    os.makedirs("../instance", exist_ok=True)
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
