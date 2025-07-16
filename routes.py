from flask import render_template, request, redirect, url_for, flash, jsonify, make_response, send_file
from app import app, db
from models import (
    Material, Product, Sale, Expense, Worker, 
    Customer, Bank, Cheque, SalesInvoice, SalesInvoiceItem,
    PurchaseInvoice, PurchaseInvoiceItem, Receipt, Payment,
    InstallmentCheque, Budget, calculate_profit_loss
)
from utils import to_jalali, from_jalali, validate_date, export_to_pdf, get_current_jalali_date
from backup_manager import (create_backup, list_backups, restore_backup, 
                           delete_backup, get_backup_info, format_file_size)
from datetime import datetime, date
from sqlalchemy import func
import json
import os

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        form_name = request.form.get('form_name')
        
        try:
            if form_name == 'material':
                name = request.form['name'].strip()
                weight = float(request.form['weight'])
                cost = float(request.form['cost'])
                date_str = request.form['date']
                
                if not name or weight <= 0 or cost <= 0 or not validate_date(date_str):
                    flash('لطفا تمام فیلدها را به درستی پر کنید', 'error')
                    return redirect(url_for('dashboard'))
                
                # Convert Jalali date to Gregorian
                gregorian_date = from_jalali(date_str)
                if not gregorian_date:
                    flash('تاریخ وارد شده نامعتبر است', 'error')
                    return redirect(url_for('dashboard'))
                
                material = Material(
                    name=name,
                    weight=weight,
                    cost=cost,
                    date=gregorian_date
                )
                db.session.add(material)
                db.session.commit()
                flash('ماده اولیه با موفقیت ثبت شد', 'success')
                
            elif form_name == 'product':
                name = request.form['name'].strip()
                count = int(request.form['count'])
                unit_cost = float(request.form['unit_cost'])
                date_str = request.form['date']
                
                if not name or count <= 0 or unit_cost <= 0 or not validate_date(date_str):
                    flash('لطفا تمام فیلدها را به درستی پر کنید', 'error')
                    return redirect(url_for('dashboard'))
                
                # Convert Jalali date to Gregorian
                gregorian_date = from_jalali(date_str)
                if not gregorian_date:
                    flash('تاریخ وارد شده نامعتبر است', 'error')
                    return redirect(url_for('dashboard'))
                
                product = Product(
                    name=name,
                    count=count,
                    unit_cost=unit_cost,
                    date=gregorian_date
                )
                db.session.add(product)
                db.session.commit()
                flash('محصول با موفقیت ثبت شد', 'success')
                
            elif form_name == 'sale':
                name = request.form['name'].strip()
                count = int(request.form['count'])
                unit_price = float(request.form['unit_price'])
                date_str = request.form['date']
                
                if not name or count <= 0 or unit_price <= 0 or not validate_date(date_str):
                    flash('لطفا تمام فیلدها را به درستی پر کنید', 'error')
                    return redirect(url_for('dashboard'))
                
                # Convert Jalali date to Gregorian
                gregorian_date = from_jalali(date_str)
                if not gregorian_date:
                    flash('تاریخ وارد شده نامعتبر است', 'error')
                    return redirect(url_for('dashboard'))
                
                sale = Sale(
                    name=name,
                    count=count,
                    unit_price=unit_price,
                    date=gregorian_date
                )
                db.session.add(sale)
                db.session.commit()
                flash('فروش با موفقیت ثبت شد', 'success')
                
            elif form_name == 'expense':
                description = request.form['desc'].strip()
                amount = float(request.form['amount'])
                date_str = request.form['date']
                
                if not description or amount <= 0 or not validate_date(date_str):
                    flash('لطفا تمام فیلدها را به درستی پر کنید', 'error')
                    return redirect(url_for('dashboard'))
                
                # Convert Jalali date to Gregorian
                gregorian_date = from_jalali(date_str)
                if not gregorian_date:
                    flash('تاریخ وارد شده نامعتبر است', 'error')
                    return redirect(url_for('dashboard'))
                
                expense = Expense(
                    description=description,
                    amount=amount,
                    date=gregorian_date
                )
                db.session.add(expense)
                db.session.commit()
                flash('هزینه با موفقیت ثبت شد', 'success')
                
            elif form_name == 'worker':
                name = request.form['name'].strip()
                amount = float(request.form['amount'])
                date_str = request.form['date']
                
                if not name or amount <= 0 or not validate_date(date_str):
                    flash('لطفا تمام فیلدها را به درستی پر کنید', 'error')
                    return redirect(url_for('dashboard'))
                
                # Convert Jalali date to Gregorian
                gregorian_date = from_jalali(date_str)
                if not gregorian_date:
                    flash('تاریخ وارد شده نامعتبر است', 'error')
                    return redirect(url_for('dashboard'))
                
                worker = Worker(
                    name=name,
                    amount=amount,
                    date=gregorian_date
                )
                db.session.add(worker)
                db.session.commit()
                flash('حقوق کارگر با موفقیت ثبت شد', 'success')
                
        except ValueError as e:
            flash('خطا در وارد کردن داده‌ها', 'error')
        except Exception as e:
            flash(f'خطا در ثبت اطلاعات: {str(e)}', 'error')
            db.session.rollback()
        
        return redirect(url_for('dashboard'))
    
    # Get data for display
    materials = Material.query.order_by(Material.date.desc()).limit(10).all()
    products = Product.query.order_by(Product.date.desc()).limit(10).all()
    sales = Sale.query.order_by(Sale.date.desc()).limit(10).all()
    expenses = Expense.query.order_by(Expense.date.desc()).limit(10).all()
    workers = Worker.query.order_by(Worker.date.desc()).limit(10).all()
    
    # Get unique names for datalists
    material_names = [name[0] for name in db.session.query(Material.name).distinct().all()]
    product_names = [name[0] for name in db.session.query(Product.name).distinct().all()]
    worker_names = [name[0] for name in db.session.query(Worker.name).distinct().all()]
    
    # Calculate basic statistics
    today = date.today()
    stats = calculate_profit_loss()
    
    return render_template('dashboard.html',
                         materials=materials,
                         products=products,
                         sales=sales,
                         expenses=expenses,
                         workers=workers,
                         material_names=material_names,
                         product_names=product_names,
                         worker_names=worker_names,
                         stats=stats,
                         to_jalali=to_jalali,
                         get_current_jalali_date=get_current_jalali_date)

@app.route('/reports')
def reports():
    # Get date range from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Calculate financial metrics
    financial_data = calculate_profit_loss(start_date_obj, end_date_obj)
    
    # Get detailed data for charts
    materials_raw = db.session.query(
        Material.date,
        func.sum(Material.cost).label('total_cost')
    ).filter(
        Material.date >= start_date_obj if start_date_obj else True,
        Material.date <= end_date_obj if end_date_obj else True
    ).group_by(Material.date).order_by(Material.date).all()
    
    sales_raw = db.session.query(
        Sale.date,
        func.sum(Sale.count * Sale.unit_price).label('total_revenue')
    ).filter(
        Sale.date >= start_date_obj if start_date_obj else True,
        Sale.date <= end_date_obj if end_date_obj else True
    ).group_by(Sale.date).order_by(Sale.date).all()
    
    # Convert to JSON-serializable format
    materials_by_date = [{'date': str(row.date), 'total_cost': float(row.total_cost)} for row in materials_raw]
    sales_by_date = [{'date': str(row.date), 'total_revenue': float(row.total_revenue)} for row in sales_raw]
    
    return render_template('reports.html',
                         financial_data=financial_data,
                         materials_by_date=materials_by_date,
                         sales_by_date=sales_by_date,
                         start_date=start_date,
                         end_date=end_date,
                         to_jalali=to_jalali)

@app.route('/export-pdf')
def export_pdf():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    financial_data = calculate_profit_loss(start_date_obj, end_date_obj)
    
    try:
        pdf_buffer = export_to_pdf(financial_data, start_date_obj, end_date_obj)
        
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=financial_report.pdf'
        
        return response
    except Exception as e:
        flash(f'خطا در تولید گزارش PDF: {str(e)}', 'error')
        return redirect(url_for('reports'))

@app.route('/api/chart-data')
def chart_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Revenue vs Expenses by month
    revenue_data = db.session.query(
        func.date_trunc('month', Sale.date).label('month'),
        func.sum(Sale.count * Sale.unit_price).label('revenue')
    ).filter(
        Sale.date >= start_date_obj if start_date_obj else True,
        Sale.date <= end_date_obj if end_date_obj else True
    ).group_by(func.date_trunc('month', Sale.date)).all()
    
    expense_data = db.session.query(
        func.date_trunc('month', Expense.date).label('month'),
        func.sum(Expense.amount).label('expenses')
    ).filter(
        Expense.date >= start_date_obj if start_date_obj else True,
        Expense.date <= end_date_obj if end_date_obj else True
    ).group_by(func.date_trunc('month', Expense.date)).all()
    
    return jsonify({
        'revenue': [{'month': str(r.month), 'value': float(r.revenue)} for r in revenue_data],
        'expenses': [{'month': str(e.month), 'value': float(e.expenses)} for e in expense_data]
    })

@app.route('/delete/<string:table>/<int:id>')
def delete_record(table, id):
    try:
        if table == 'material':
            record = Material.query.get_or_404(id)
        elif table == 'product':
            record = Product.query.get_or_404(id)
        elif table == 'sale':
            record = Sale.query.get_or_404(id)
        elif table == 'expense':
            record = Expense.query.get_or_404(id)
        elif table == 'worker':
            record = Worker.query.get_or_404(id)
        else:
            flash('نوع رکورد نامعتبر است', 'error')
            return redirect(url_for('dashboard'))
        
        db.session.delete(record)
        db.session.commit()
        flash('رکورد با موفقیت حذف شد', 'success')
        
    except Exception as e:
        flash(f'خطا در حذف رکورد: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('dashboard'))

# Backup and Restore Routes
@app.route('/backup')
def backup_management():
    """Backup management page"""
    backups = list_backups()
    
    # Add Persian date formatting and file size formatting
    for backup in backups:
        if 'created_at' in backup:
            try:
                created_date = datetime.fromisoformat(backup['created_at'].replace('Z', '+00:00'))
                backup['created_at_jalali'] = to_jalali(created_date.date())
                backup['created_time'] = created_date.strftime('%H:%M')
            except:
                backup['created_at_jalali'] = 'نامعلوم'
                backup['created_time'] = ''
        
        if 'file_size' in backup:
            backup['file_size_formatted'] = format_file_size(backup['file_size'])
    
    return render_template('backup.html', backups=backups, to_jalali=to_jalali)

@app.route('/backup/create', methods=['POST'])
def create_backup_route():
    """Create a new backup"""
    try:
        backup_name = request.form.get('backup_name', '').strip()
        result = create_backup(backup_name if backup_name else None)
        
        if result['success']:
            flash(f'پشتیبان با موفقیت ایجاد شد: {result["filename"]}', 'success')
        else:
            flash(f'خطا در ایجاد پشتیبان: {result["error"]}', 'error')
            
    except Exception as e:
        flash(f'خطا در ایجاد پشتیبان: {str(e)}', 'error')
    
    return redirect(url_for('backup_management'))

@app.route('/backup/restore/<filename>', methods=['POST'])
def restore_backup_route(filename):
    """Restore from a backup"""
    try:
        result = restore_backup(filename)
        
        if result['success']:
            restored_counts = result.get('restored_counts', {})
            counts_str = ', '.join([f'{k}: {v}' for k, v in restored_counts.items()])
            flash(f'داده‌ها با موفقیت بازیابی شد ({counts_str})', 'success')
        else:
            flash(f'خطا در بازیابی: {result["error"]}', 'error')
            
    except Exception as e:
        flash(f'خطا در بازیابی: {str(e)}', 'error')
    
    return redirect(url_for('backup_management'))

@app.route('/backup/download/<filename>')
def download_backup(filename):
    """Download a backup file"""
    try:
        backup_path = os.path.join('backups', filename)
        if os.path.exists(backup_path):
            return send_file(backup_path, as_attachment=True, download_name=filename)
        else:
            flash('فایل پشتیبان یافت نشد', 'error')
            return redirect(url_for('backup_management'))
    except Exception as e:
        flash(f'خطا در دانلود: {str(e)}', 'error')
        return redirect(url_for('backup_management'))

@app.route('/backup/delete/<filename>', methods=['POST'])
def delete_backup_route(filename):
    """Delete a backup file"""
    try:
        result = delete_backup(filename)
        
        if result['success']:
            flash('پشتیبان با موفقیت حذف شد', 'success')
        else:
            flash(f'خطا در حذف پشتیبان: {result["error"]}', 'error')
            
    except Exception as e:
        flash(f'خطا در حذف پشتیبان: {str(e)}', 'error')
    
    return redirect(url_for('backup_management'))

@app.route('/backup/upload', methods=['POST'])
def upload_backup():
    """Upload and restore from backup file"""
    try:
        if 'backup_file' not in request.files:
            flash('فایلی انتخاب نشده است', 'error')
            return redirect(url_for('backup_management'))
        
        file = request.files['backup_file']
        if file.filename == '':
            flash('فایلی انتخاب نشده است', 'error')
            return redirect(url_for('backup_management'))
        
        if file and file.filename.endswith('.zip'):
            # Save uploaded file temporarily
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
                file.save(temp_file.name)
                
                # Create a copy in backups directory
                filename = f"uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                backup_path = os.path.join('backups', filename)
                
                if not os.path.exists('backups'):
                    os.makedirs('backups')
                
                import shutil
                shutil.copy2(temp_file.name, backup_path)
                os.unlink(temp_file.name)
                
                flash(f'فایل با موفقیت آپلود شد: {filename}', 'success')
        else:
            flash('فقط فایل‌های ZIP پشتیبانی می‌شوند', 'error')
            
    except Exception as e:
        flash(f'خطا در آپلود فایل: {str(e)}', 'error')
    
    return redirect(url_for('backup_management'))

# فاکتورهای فروش
@app.route('/sales_invoices')
def sales_invoices():
    invoices = SalesInvoice.query.order_by(SalesInvoice.date.desc()).all()
    customers = Customer.query.all()
    return render_template('sales_invoices.html', invoices=invoices, customers=customers)

@app.route('/sales_invoices/create', methods=['GET', 'POST'])
def create_sales_invoice():
    if request.method == 'POST':
        try:
            invoice_number = request.form['invoice_number']
            customer_id = int(request.form['customer_id'])
            date_str = request.form['date']
            
            # تبدیل تاریخ شمسی به میلادی
            try:
                date = from_jalali(date_str)
            except:
                flash('فرمت تاریخ صحیح نیست. از فرمت ۱۴۰۳/۰۱/۰۱ استفاده کنید.', 'error')
                return redirect(url_for('sales_invoices'))
            
            total_amount = float(request.form['total_amount'])
            discount = float(request.form.get('discount', 0))
            tax = float(request.form.get('tax', 0))
            final_amount = total_amount - discount + tax
            status = request.form.get('status', 'معلق')
            notes = request.form.get('notes', '')
            
            invoice = SalesInvoice(
                invoice_number=invoice_number,
                customer_id=customer_id,
                date=date,
                total_amount=total_amount,
                discount=discount,
                tax=tax,
                final_amount=final_amount,
                status=status,
                notes=notes
            )
            
            db.session.add(invoice)
            db.session.commit()
            flash('فاکتور فروش با موفقیت ایجاد شد!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطا در ایجاد فاکتور: {str(e)}', 'error')
    
    return redirect(url_for('sales_invoices'))

# فاکتورهای خرید
@app.route('/purchase_invoices')
def purchase_invoices():
    invoices = PurchaseInvoice.query.order_by(PurchaseInvoice.date.desc()).all()
    return render_template('purchase_invoices.html', invoices=invoices)

@app.route('/purchase_invoices/create', methods=['POST'])
def create_purchase_invoice():
    try:
        invoice_number = request.form['invoice_number']
        supplier_name = request.form['supplier_name']
        date_str = request.form['date']
        
        # تبدیل تاریخ شمسی به میلادی
        try:
            date = from_jalali(date_str)
        except:
            flash('فرمت تاریخ صحیح نیست. از فرمت ۱۴۰۳/۰۱/۰۱ استفاده کنید.', 'error')
            return redirect(url_for('purchase_invoices'))
        
        total_amount = float(request.form['total_amount'])
        discount = float(request.form.get('discount', 0))
        tax = float(request.form.get('tax', 0))
        final_amount = total_amount - discount + tax
        status = request.form.get('status', 'معلق')
        notes = request.form.get('notes', '')
        
        invoice = PurchaseInvoice(
            invoice_number=invoice_number,
            supplier_name=supplier_name,
            date=date,
            total_amount=total_amount,
            discount=discount,
            tax=tax,
            final_amount=final_amount,
            status=status,
            notes=notes
        )
        
        db.session.add(invoice)
        db.session.commit()
        flash('فاکتور خرید با موفقیت ایجاد شد!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'خطا در ایجاد فاکتور: {str(e)}', 'error')
    
    return redirect(url_for('purchase_invoices'))

# مدیریت مشتریان
@app.route('/customers')
def customers():
    customers_list = Customer.query.all()
    return render_template('customers.html', customers=customers_list)

@app.route('/customers/create', methods=['POST'])
def create_customer():
    try:
        name = request.form['name']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        email = request.form.get('email', '')
        national_code = request.form.get('national_code', '')
        company_name = request.form.get('company_name', '')
        
        customer = Customer(
            name=name,
            phone=phone,
            address=address,
            email=email,
            national_code=national_code,
            company_name=company_name
        )
        
        db.session.add(customer)
        db.session.commit()
        flash('مشتری با موفقیت اضافه شد!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'خطا در اضافه کردن مشتری: {str(e)}', 'error')
    
    return redirect(url_for('customers'))

# مدیریت بانک‌ها
@app.route('/banks')
def banks():
    banks_list = Bank.query.all()
    return render_template('banks.html', banks=banks_list)

@app.route('/banks/create', methods=['POST'])
def create_bank():
    try:
        name = request.form['name']
        account_number = request.form.get('account_number', '')
        shaba_number = request.form.get('shaba_number', '')
        card_number = request.form.get('card_number', '')
        balance = float(request.form.get('balance', 0))
        
        bank = Bank(
            name=name,
            account_number=account_number,
            shaba_number=shaba_number,
            card_number=card_number,
            balance=balance
        )
        
        db.session.add(bank)
        db.session.commit()
        flash('بانک با موفقیت اضافه شد!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'خطا در اضافه کردن بانک: {str(e)}', 'error')
    
    return redirect(url_for('banks'))

# مدیریت چک‌ها
@app.route('/cheques')
def cheques():
    cheques_list = Cheque.query.order_by(Cheque.due_date.desc()).all()
    customers = Customer.query.all()
    banks = Bank.query.all()
    return render_template('cheques.html', cheques=cheques_list, customers=customers, banks=banks)

@app.route('/cheques/create', methods=['POST'])
def create_cheque():
    try:
        cheque_number = request.form['cheque_number']
        customer_id = int(request.form['customer_id'])
        bank_id = int(request.form['bank_id'])
        amount = float(request.form['amount'])
        issue_date_str = request.form['issue_date']
        due_date_str = request.form['due_date']
        status = request.form.get('status', 'در انتظار')
        description = request.form.get('description', '')
        
        # تبدیل تاریخ‌های شمسی به میلادی
        try:
            issue_date = from_jalali(issue_date_str)
            due_date = from_jalali(due_date_str)
        except:
            flash('فرمت تاریخ صحیح نیست. از فرمت ۱۴۰۳/۰۱/۰۱ استفاده کنید.', 'error')
            return redirect(url_for('cheques'))
        
        cheque = Cheque(
            cheque_number=cheque_number,
            customer_id=customer_id,
            bank_id=bank_id,
            amount=amount,
            issue_date=issue_date,
            due_date=due_date,
            status=status,
            description=description
        )
        
        db.session.add(cheque)
        db.session.commit()
        flash('چک با موفقیت اضافه شد!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'خطا در اضافه کردن چک: {str(e)}', 'error')
    
    return redirect(url_for('cheques'))

@app.route('/cheques/<int:cheque_id>/edit', methods=['POST'])
def edit_cheque(cheque_id):
    try:
        cheque = Cheque.query.get_or_404(cheque_id)
        
        cheque.cheque_number = request.form['cheque_number']
        cheque.customer_id = int(request.form['customer_id'])
        cheque.bank_id = int(request.form['bank_id'])
        cheque.amount = float(request.form['amount'])
        cheque.status = request.form.get('status', 'در انتظار')
        cheque.description = request.form.get('description', '')
        
        # تبدیل تاریخ‌های شمسی به میلادی
        try:
            cheque.issue_date = from_jalali(request.form['issue_date'])
            cheque.due_date = from_jalali(request.form['due_date'])
        except:
            flash('فرمت تاریخ صحیح نیست. از فرمت ۱۴۰۳/۰۱/۰۱ استفاده کنید.', 'error')
            return redirect(url_for('cheques'))
        
        db.session.commit()
        flash('چک با موفقیت ویرایش شد!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'خطا در ویرایش چک: {str(e)}', 'error')
    
    return redirect(url_for('cheques'))

@app.route('/cheques/<int:cheque_id>', methods=['DELETE'])
def delete_cheque(cheque_id):
    try:
        cheque = Cheque.query.get_or_404(cheque_id)
        db.session.delete(cheque)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/cheques/<int:cheque_id>/status', methods=['POST'])
def update_cheque_status(cheque_id):
    try:
        cheque = Cheque.query.get_or_404(cheque_id)
        new_status = request.json.get('status')
        
        if new_status in ['در انتظار', 'نقد شده', 'برگشتی']:
            cheque.status = new_status
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'وضعیت نامعتبر است'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/banks/<int:bank_id>/edit', methods=['POST'])
def edit_bank(bank_id):
    try:
        bank = Bank.query.get_or_404(bank_id)
        
        bank.name = request.form['name']
        bank.account_number = request.form.get('account_number', '')
        bank.shaba_number = request.form.get('shaba_number', '')
        bank.card_number = request.form.get('card_number', '')
        bank.balance = float(request.form.get('balance', 0))
        
        db.session.commit()
        flash('بانک با موفقیت ویرایش شد!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'خطا در ویرایش بانک: {str(e)}', 'error')
    
    return redirect(url_for('banks'))

@app.route('/customers/<int:customer_id>/edit', methods=['POST'])
def edit_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        customer.name = request.form['name']
        customer.phone = request.form.get('phone', '')
        customer.address = request.form.get('address', '')
        customer.email = request.form.get('email', '')
        customer.national_code = request.form.get('national_code', '')
        customer.company_name = request.form.get('company_name', '')
        
        db.session.commit()
        flash('مشتری با موفقیت ویرایش شد!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'خطا در ویرایش مشتری: {str(e)}', 'error')
    
    return redirect(url_for('customers'))

@app.route('/budgets/<int:budget_id>/edit', methods=['POST'])
def edit_budget(budget_id):
    try:
        budget = Budget.query.get_or_404(budget_id)
        
        budget.category = request.form['category']
        budget.planned_amount = float(request.form['planned_amount'])
        budget.actual_amount = float(request.form.get('actual_amount', 0))
        budget.description = request.form.get('description', '')
        
        # Convert Jalali dates to Gregorian
        try:
            budget.period_start = from_jalali(request.form['period_start'])
            budget.period_end = from_jalali(request.form['period_end'])
        except:
            flash('فرمت تاریخ صحیح نیست. از فرمت ۱۴۰۳/۰۱/۰۱ استفاده کنید.', 'error')
            return redirect(url_for('budgets'))
        
        db.session.commit()
        flash('بودجه با موفقیت ویرایش شد!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'خطا در ویرایش بودجه: {str(e)}', 'error')
    
    return redirect(url_for('budgets'))

# دریافتی‌ها
@app.route('/receipts')
def receipts():
    receipts_list = Receipt.query.order_by(Receipt.date.desc()).all()
    customers = Customer.query.all()
    banks = Bank.query.all()
    return render_template('receipts.html', receipts=receipts_list, customers=customers, banks=banks)

# پرداختی‌ها
@app.route('/payments')
def payments():
    payments_list = Payment.query.order_by(Payment.date.desc()).all()
    banks = Bank.query.all()
    return render_template('payments.html', payments=payments_list, banks=banks)

# چک‌های اقساطی
@app.route('/installment_cheques', methods=['GET', 'POST'])
def installment_cheques():
    if request.method == 'POST':
        try:
            customer_id = request.form['customer_id']
            total_amount = float(request.form['total_amount'])
            installment_count = int(request.form['installment_count'])
            start_date_str = request.form['start_date']
            description = request.form.get('description', '')
            
            # Convert Jalali date to Gregorian
            try:
                start_date = from_jalali(start_date_str)
            except:
                flash('فرمت تاریخ صحیح نیست. از فرمت ۱۴۰۳/۰۱/۰۱ استفاده کنید.', 'error')
                return redirect(url_for('installment_cheques'))
            
            # Calculate installment amount
            installment_amount = total_amount / installment_count
            
            installment = InstallmentCheque(
                customer_id=customer_id,
                total_amount=total_amount,
                installment_count=installment_count,
                installment_amount=installment_amount,
                start_date=start_date,
                description=description
            )
            
            db.session.add(installment)
            db.session.commit()
            flash('چک اقساطی با موفقیت اضافه شد!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطا در ایجاد چک اقساطی: {str(e)}', 'error')
    
    installments = InstallmentCheque.query.order_by(InstallmentCheque.start_date.desc()).all()
    customers = Customer.query.all()
    return render_template('installment_cheques.html', installments=installments, customers=customers)

# بودجه‌بندی
@app.route('/budgets')
def budgets():
    budgets_list = Budget.query.order_by(Budget.period_start.desc()).all()
    return render_template('budgets.html', budgets=budgets_list)

# Route های حذف
@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/banks/<int:bank_id>', methods=['DELETE'])
def delete_bank(bank_id):
    try:
        bank = Bank.query.get_or_404(bank_id)
        db.session.delete(bank)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/budgets/<int:budget_id>', methods=['DELETE'])
def delete_budget(budget_id):
    try:
        budget = Budget.query.get_or_404(budget_id)
        db.session.delete(budget)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/budgets/create', methods=['POST'])
def create_budget():
    try:
        category = request.form['category']
        planned_amount = float(request.form['planned_amount'])
        period_start_str = request.form['period_start']
        period_end_str = request.form['period_end']
        description = request.form.get('description', '')
        
        # تبدیل تاریخ‌های شمسی به میلادی
        try:
            period_start = from_jalali(period_start_str)
            period_end = from_jalali(period_end_str)
        except:
            flash('فرمت تاریخ صحیح نیست. از فرمت ۱۴۰۳/۰۱/۰۱ استفاده کنید.', 'error')
            return redirect(url_for('budgets'))
        
        budget = Budget(
            category=category,
            planned_amount=planned_amount,
            period_start=period_start,
            period_end=period_end,
            description=description
        )
        
        db.session.add(budget)
        db.session.commit()
        flash('بودجه با موفقیت اضافه شد!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'خطا در اضافه کردن بودجه: {str(e)}', 'error')
    
    return redirect(url_for('budgets'))

# Delete routes for invoices
@app.route('/sales_invoices/<int:invoice_id>', methods=['DELETE'])
def delete_sales_invoice(invoice_id):
    try:
        invoice = SalesInvoice.query.get_or_404(invoice_id)
        # Delete related items first
        SalesInvoiceItem.query.filter_by(invoice_id=invoice_id).delete()
        db.session.delete(invoice)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/purchase_invoices/<int:invoice_id>', methods=['DELETE'])
def delete_purchase_invoice(invoice_id):
    try:
        invoice = PurchaseInvoice.query.get_or_404(invoice_id)
        # Delete related items first
        PurchaseInvoiceItem.query.filter_by(invoice_id=invoice_id).delete()
        db.session.delete(invoice)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# Additional delete routes
@app.route('/installment_cheques/<int:cheque_id>', methods=['DELETE'])
def delete_installment_cheque(cheque_id):
    try:
        cheque = InstallmentCheque.query.get_or_404(cheque_id)
        db.session.delete(cheque)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/receipts/<int:receipt_id>', methods=['DELETE'])
def delete_receipt(receipt_id):
    try:
        receipt = Receipt.query.get_or_404(receipt_id)
        db.session.delete(receipt)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    try:
        payment = Payment.query.get_or_404(payment_id)
        db.session.delete(payment)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
