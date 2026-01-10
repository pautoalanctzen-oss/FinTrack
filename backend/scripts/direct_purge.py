import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "users.db")

def purge_user_data(username: str, apply: bool = False):
    """Purge all data for a user directly from DB."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        conn.row_factory = sqlite3.Row
        
        # Get user_id
        cursor = conn.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            print(f"User {username} not found")
            return
        
        user_id = user["id"]
        
        # Count what will be deleted
        counts = {}
        for table in ["registros", "clientes", "obras", "productos"]:
            c = conn.execute(f"SELECT COUNT(*) as cnt FROM {table} WHERE user_id = ?", (user_id,)).fetchone()
            counts[table] = c["cnt"]
        
        print(f"Will delete: {counts}")
        
        if apply:
            conn.execute("DELETE FROM registros WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM clientes WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM obras WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM productos WHERE user_id = ?", (user_id,))
            conn.commit()
            print("Deleted successfully")
        
        conn.close()
        return counts
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    import sys
    apply = "--apply" in sys.argv
    purge_user_data("Panchita's Catering", apply=apply)
