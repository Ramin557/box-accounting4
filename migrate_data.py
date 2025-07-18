import os
import jdatetime
from app import app, db
from models import (
    Material, Product, Sale, Expense, Worker, Cheque, SalesInvoice,
    PurchaseInvoice, Receipt, Payment, InstallmentCheque, Budget
)

def to_jalali_str(date_obj):
    """Converts a date object to a Jalali date string."""
    if not date_obj:
        return None
    return jdatetime.date.fromgregorian(date=date_obj).strftime('%Y/%m/%d')

def migrate_table(model, date_column_name='date', jdate_column_name='jdate'):
    """Migrates a single table to add Jalali dates."""
    print(f"Migrating {model.__tablename__}...")
    records = model.query.all()
    updated_count = 0
    for record in records:
        gregorian_date = getattr(record, date_column_name)
        if gregorian_date and not getattr(record, jdate_column_name):
            jalali_date_str = to_jalali_str(gregorian_date)
            setattr(record, jdate_column_name, jalali_date_str)
            updated_count += 1
    db.session.commit()
    print(f"Updated {updated_count} records in {model.__tablename__}.")

def migrate_cheque_table():
    """Migrates the Cheque table which has multiple date columns."""
    print("Migrating cheques...")
    records = Cheque.query.all()
    updated_count = 0
    for record in records:
        updated = False
        if record.issue_date and not record.j_issue_date:
            record.j_issue_date = to_jalali_str(record.issue_date)
            updated = True
        if record.due_date and not record.j_due_date:
            record.j_due_date = to_jalali_str(record.due_date)
            updated = True
        if updated:
            updated_count += 1
    db.session.commit()
    print(f"Updated {updated_count} records in cheques.")

def migrate_installment_cheque_table():
    """Migrates the InstallmentCheque table."""
    print("Migrating installment_cheques...")
    records = InstallmentCheque.query.all()
    updated_count = 0
    for record in records:
        if record.start_date and not record.j_start_date:
            record.j_start_date = to_jalali_str(record.start_date)
            updated_count += 1
    db.session.commit()
    print(f"Updated {updated_count} records in installment_cheques.")

def migrate_budget_table():
    """Migrates the Budget table."""
    print("Migrating budgets...")
    records = Budget.query.all()
    updated_count = 0
    for record in records:
        updated = False
        if record.period_start and not record.j_period_start:
            record.j_period_start = to_jalali_str(record.period_start)
            updated = True
        if record.period_end and not record.j_period_end:
            record.j_period_end = to_jalali_str(record.period_end)
            updated = True
        if updated:
            updated_count += 1
    db.session.commit()
    print(f"Updated {updated_count} records in budgets.")


def run_migration():
    """Runs the full data migration."""
    with app.app_context():
        migrate_table(Material)
        migrate_table(Product)
        migrate_table(Sale)
        migrate_table(Expense)
        migrate_table(Worker)
        migrate_table(SalesInvoice)
        migrate_table(PurchaseInvoice)
        migrate_table(Receipt)
        migrate_table(Payment)

        migrate_cheque_table()
        migrate_installment_cheque_table()
        migrate_budget_table()

        print("\nMigration complete!")

if __name__ == '__main__':
    run_migration()
