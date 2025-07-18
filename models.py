from app import db
from datetime import datetime
from sqlalchemy import func

class Material(db.Model):
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, nullable=False, default=0)  # وزن به کیلوگرم
    cost = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    jdate = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Material {self.name}>'

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    jdate = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def total_cost(self):
        return self.count * self.unit_cost
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Sale(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    jdate = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def total_revenue(self):
        return self.count * self.unit_price
    
    def __repr__(self):
        return f'<Sale {self.name}>'

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    jdate = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Expense {self.description}>'

class Worker(db.Model):
    __tablename__ = 'workers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    jdate = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Worker {self.name}>'

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    email = db.Column(db.String(120))
    national_code = db.Column(db.String(15))  # کد ملی
    company_name = db.Column(db.String(200))  # نام شرکت
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Customer {self.name}>'

class Bank(db.Model):
    __tablename__ = 'banks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(50))
    shaba_number = db.Column(db.String(30))  # شماره شبا
    card_number = db.Column(db.String(20))   # شماره کارت
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Bank {self.name}>'

class Cheque(db.Model):
    __tablename__ = 'cheques'
    
    id = db.Column(db.Integer, primary_key=True)
    cheque_number = db.Column(db.String(50), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'))
    amount = db.Column(db.Float, nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    j_issue_date = db.Column(db.String(10), nullable=True)
    due_date = db.Column(db.Date, nullable=False)
    j_due_date = db.Column(db.String(10), nullable=True)
    status = db.Column(db.String(20), default='در انتظار')  # در انتظار، نقد شده، برگشتی
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref='cheques')
    bank = db.relationship('Bank', backref='cheques')
    
    def __repr__(self):
        return f'<Cheque {self.cheque_number}>'

class SalesInvoice(db.Model):
    """فاکتور فروش"""
    __tablename__ = 'sales_invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    date = db.Column(db.Date, nullable=False)
    jdate = db.Column(db.String(10), nullable=True)
    total_amount = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    tax = db.Column(db.Float, default=0.0)
    final_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='معلق')  # معلق، تأیید شده، لغو شده
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    customer = db.relationship('Customer', backref='sales_invoices')
    
    def __repr__(self):
        return f'<SalesInvoice {self.invoice_number}>'

class SalesInvoiceItem(db.Model):
    """آیتم‌های فاکتور فروش"""
    __tablename__ = 'sales_invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('sales_invoices.id'))
    product_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    # Relations
    invoice = db.relationship('SalesInvoice', backref='items')

class PurchaseInvoice(db.Model):
    """فاکتور خرید"""
    __tablename__ = 'purchase_invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    jdate = db.Column(db.String(10), nullable=True)
    total_amount = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    tax = db.Column(db.Float, default=0.0)
    final_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='معلق')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PurchaseInvoiceItem(db.Model):
    """آیتم‌های فاکتور خرید"""
    __tablename__ = 'purchase_invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('purchase_invoices.id'))
    material_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    # Relations
    invoice = db.relationship('PurchaseInvoice', backref='items')

class Receipt(db.Model):
    """دریافتی"""
    __tablename__ = 'receipts'
    
    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    jdate = db.Column(db.String(10), nullable=True)
    payment_method = db.Column(db.String(50))  # نقد، چک، انتقال بانکی
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    customer = db.relationship('Customer', backref='receipts')
    bank = db.relationship('Bank', backref='receipts')

class Payment(db.Model):
    """پرداختی"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_number = db.Column(db.String(50), unique=True, nullable=False)
    recipient = db.Column(db.String(200), nullable=False)  # دریافت کننده
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    jdate = db.Column(db.String(10), nullable=True)
    payment_method = db.Column(db.String(50))
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    bank = db.relationship('Bank', backref='payments')

class InstallmentCheque(db.Model):
    """چک اقساطی"""
    __tablename__ = 'installment_cheques'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    total_amount = db.Column(db.Float, nullable=False)
    installment_count = db.Column(db.Integer, nullable=False)
    installment_amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    j_start_date = db.Column(db.String(10), nullable=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    customer = db.relationship('Customer', backref='installment_cheques')

class Budget(db.Model):
    """بودجه بندی"""
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)  # دسته بندی بودجه
    planned_amount = db.Column(db.Float, nullable=False)  # مبلغ برنامه ریزی شده
    actual_amount = db.Column(db.Float, default=0.0)      # مبلغ واقعی
    period_start = db.Column(db.Date, nullable=False)     # شروع دوره
    j_period_start = db.Column(db.String(10), nullable=True)
    period_end = db.Column(db.Date, nullable=False)       # پایان دوره
    j_period_end = db.Column(db.String(10), nullable=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper functions for business analytics
def get_total_materials_cost(start_date=None, end_date=None):
    query = db.session.query(func.sum(Material.cost))
    if start_date:
        query = query.filter(Material.date >= start_date)
    if end_date:
        query = query.filter(Material.date <= end_date)
    result = query.scalar()
    return result or 0

def get_total_production_cost(start_date=None, end_date=None):
    query = db.session.query(func.sum(Product.count * Product.unit_cost))
    if start_date:
        query = query.filter(Product.date >= start_date)
    if end_date:
        query = query.filter(Product.date <= end_date)
    result = query.scalar()
    return result or 0

def get_total_revenue(start_date=None, end_date=None):
    query = db.session.query(func.sum(Sale.count * Sale.unit_price))
    if start_date:
        query = query.filter(Sale.date >= start_date)
    if end_date:
        query = query.filter(Sale.date <= end_date)
    result = query.scalar()
    return result or 0

def get_total_expenses(start_date=None, end_date=None):
    query = db.session.query(func.sum(Expense.amount))
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    result = query.scalar()
    return result or 0

def get_total_worker_wages(start_date=None, end_date=None):
    query = db.session.query(func.sum(Worker.amount))
    if start_date:
        query = query.filter(Worker.date >= start_date)
    if end_date:
        query = query.filter(Worker.date <= end_date)
    result = query.scalar()
    return result or 0

def calculate_profit_loss(start_date=None, end_date=None):
    revenue = get_total_revenue(start_date, end_date)
    materials_cost = get_total_materials_cost(start_date, end_date)
    production_cost = get_total_production_cost(start_date, end_date)
    expenses = get_total_expenses(start_date, end_date)
    worker_wages = get_total_worker_wages(start_date, end_date)
    
    total_costs = materials_cost + production_cost + expenses + worker_wages
    profit_loss = revenue - total_costs
    
    return {
        'revenue': revenue,
        'materials_cost': materials_cost,
        'production_cost': production_cost,
        'expenses': expenses,
        'worker_wages': worker_wages,
        'total_costs': total_costs,
        'profit_loss': profit_loss
    }