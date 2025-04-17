from flask import Flask, render_template, request, redirect, send_file
import os
import csv
import io
from datetime import datetime

app = Flask(__name__)
ORDERS_FILE = 'orders.txt'

def load_orders():
    orders = []
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f):
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    username = parts[0]
                    amount = parts[1]
                    processed = parts[2] if len(parts) > 2 else '0'
                    orders.append({'id': idx, 'username': username, 'amount': amount, 'processed': processed})
    return orders

def save_orders(orders):
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        for order in orders:
            f.write(f"{order['username']}|{order['amount']}|{order['processed']}\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    username = request.form['username']
    amount = request.form['amount']
    with open(ORDERS_FILE, 'a', encoding='utf-8') as f:
        f.write(f'{username}|{amount}|0\n')  # 0 là chưa xử lý
    return render_template('thankyou.html', username=username, amount=amount)

@app.route('/orders')
def orders():
    orders = load_orders()
    return render_template('orders.html', orders=orders)

@app.route('/delete/<int:order_id>')
def delete_order(order_id):
    orders = load_orders()
    if 0 <= order_id < len(orders):
        orders.pop(order_id)
        save_orders(orders)
    return redirect('/orders')

@app.route('/toggle/<int:order_id>')
def toggle_order(order_id):
    orders = load_orders()
    if 0 <= order_id < len(orders):
        orders[order_id]['processed'] = '1' if orders[order_id]['processed'] == '0' else '0'
        save_orders(orders)
    return redirect('/orders')

@app.route('/export')
def export_orders():
    orders = load_orders()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Username', 'Amount', 'Processed'])
    for order in orders:
        writer.writerow([order['username'], order['amount'], 'Yes' if order['processed'] == '1' else 'No'])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    output.close()

    filename = f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(mem, mimetype='text/csv', as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(debug=True)
