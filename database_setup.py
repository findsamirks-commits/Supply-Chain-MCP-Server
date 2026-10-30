"""Database setup script for Enterprise Supply Chain ERP.

Initializes retail_erp.db with inventory and vendor_lead_times tables
populated with synthetic quick-commerce dark store replenishment data.
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "retail_erp.db")


def initialize_database():
    """Creates tables and inserts synthetic records into retail_erp.db."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table 1: Inventory
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS inventory (
            sku TEXT NOT NULL,
            dark_store_id TEXT NOT NULL,
            stock_level INTEGER NOT NULL,
            PRIMARY KEY (sku, dark_store_id)
        );
        """
    )

    # Table 2: Vendor Lead Times
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vendor_lead_times (
            vendor_id TEXT NOT NULL,
            category TEXT NOT NULL,
            lead_time_days INTEGER NOT NULL,
            PRIMARY KEY (vendor_id, category)
        );
        """
    )

    # Clear previous seed records for clean idempotent runs
    cursor.execute("DELETE FROM inventory;")
    cursor.execute("DELETE FROM vendor_lead_times;")

    # Insert 5 rows of inventory data
    inventory_records = [
        ("SKU-AMUL-BUTTER-500G", "DARKSTORE-DELHI-SOUTH-01", 142),
        ("SKU-AASHIRVAAD-ATTA-5KG", "DARKSTORE-DELHI-SOUTH-01", 38),
        ("SKU-NESTLE-MILKMAID-400G", "DARKSTORE-DELHI-SOUTH-01", 0),  # OOS scenario
        ("SKU-MOTHERDAIRY-GHEE-1L", "DARKSTORE-GURGAON-HUB-04", 65),
        ("SKU-BRITANNIA-CHEESE-200G", "DARKSTORE-GURGAON-HUB-04", 19),
    ]
    cursor.executemany(
        "INSERT INTO inventory (sku, dark_store_id, stock_level) VALUES (?, ?, ?);",
        inventory_records,
    )

    # Insert 5 rows of vendor lead time data
    vendor_records = [
        ("VENDOR-AMUL-DIRECT", "Dairy & Spreads", 2),
        ("VENDOR-ITC-LIMITED", "Staples & Flours", 4),
        ("VENDOR-NESTLE-INDIA", "Packaged Foods & Dairy", 3),
        ("VENDOR-MOTHER-DAIRY", "Fresh Dairy & Edible Oils", 1),
        ("VENDOR-BRITANNIA-IND", "Bakery & Cheese", 5),
    ]
    cursor.executemany(
        "INSERT INTO vendor_lead_times (vendor_id, category, lead_time_days) VALUES (?, ?, ?);",
        vendor_records,
    )

    conn.commit()
    conn.close()
    print(f"[OK] Successfully initialized {DB_PATH}")
    print(f"[OK] Populated {len(inventory_records)} inventory rows.")
    print(f"[OK] Populated {len(vendor_records)} vendor lead time rows.")


if __name__ == "__main__":
    initialize_database()
