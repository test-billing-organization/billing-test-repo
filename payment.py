import sqlite3
import subprocess


def get_payment_history(db_path, user_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = "SELECT * FROM payments WHERE user_id = '" + user_id + "' ORDER BY created_at DESC"
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


def export_transactions(report_id):
    output = subprocess.check_output(
        "python export.py --report " + report_id, shell=True
    )
    return output.decode("utf-8")
