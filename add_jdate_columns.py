import sqlite3

def add_column_if_not_exists(db_path, table_name, column_name, column_type):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [info[1] for info in cursor.fetchall()]

        if column_name not in columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            print(f"Added column '{column_name}' to table '{table_name}'.")
        else:
            print(f"Column '{column_name}' already exists in table '{table_name}'.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    db_file = 'instance/accounting.db'

    tables_with_dates = {
        'materials': [('jdate', 'VARCHAR(10)')],
        'products': [('jdate', 'VARCHAR(10)')],
        'sales': [('jdate', 'VARCHAR(10)')],
        'expenses': [('jdate', 'VARCHAR(10)')],
        'workers': [('jdate', 'VARCHAR(10)')],
        'cheques': [('j_issue_date', 'VARCHAR(10)'), ('j_due_date', 'VARCHAR(10)')],
        'sales_invoices': [('jdate', 'VARCHAR(10)')],
        'purchase_invoices': [('jdate', 'VARCHAR(10)')],
        'receipts': [('jdate', 'VARCHAR(10)')],
        'payments': [('jdate', 'VARCHAR(10)')],
        'installment_cheques': [('j_start_date', 'VARCHAR(10)')],
        'budgets': [('j_period_start', 'VARCHAR(10)'), ('j_period_end', 'VARCHAR(10)')]
    }

    for table, columns in tables_with_dates.items():
        for col_name, col_type in columns:
            add_column_if_not_exists(db_file, table, col_name, col_type)
