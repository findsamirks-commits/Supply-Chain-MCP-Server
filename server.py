"""Enterprise Supply Chain Model Context Protocol (MCP) Server.

Exposes standard JSON-RPC tools over stdio for secure retail ERP data access
by MCP-compatible agent runtimes (Claude Desktop, Antigravity IDE, Cursor, etc.).
"""

import json
import os
import sqlite3
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Path to the SQLite retail ERP database
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "retail_erp.db")

# Initialize the FastMCP server
mcp = FastMCP("enterprise-supply-chain-erp")


def get_db_connection() -> sqlite3.Connection:
    """Creates a read-only SQLite database connection."""
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def get_inventory_level(sku: str, dark_store_id: str) -> str:
    """Retrieve the current on-hand inventory stock level for a SKU at a designated dark store.

    Args:
        sku: The retail SKU identifier (e.g., 'SKU-AMUL-BUTTER-500G')
        dark_store_id: The fulfillment hub identifier (e.g., 'DARKSTORE-DELHI-SOUTH-01')

    Returns:
        JSON string containing the SKU, dark store ID, stock level, and operational stock status.
    """
    clean_sku = sku.strip().upper()
    clean_dark_store = dark_store_id.strip().upper()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT sku, dark_store_id, stock_level
            FROM inventory
            WHERE UPPER(sku) = ? AND UPPER(dark_store_id) = ?;
            """,
            (clean_sku, clean_dark_store),
        )
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return json.dumps(
                {
                    "error": "RecordNotFound",
                    "sku": sku,
                    "dark_store_id": dark_store_id,
                    "message": f"No inventory record found for SKU '{sku}' at Dark Store '{dark_store_id}'.",
                },
                indent=2,
            )

        stock_level = row["stock_level"]
        status = "CRITICAL_OOS" if stock_level == 0 else ("LOW_STOCK" if stock_level < 25 else "HEALTHY")

        return json.dumps(
            {
                "sku": row["sku"],
                "dark_store_id": row["dark_store_id"],
                "stock_level": stock_level,
                "status": status,
                "reorder_recommended": stock_level < 25,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"error": "DatabaseQueryError", "details": str(e)},
            indent=2,
        )


@mcp.tool()
def get_vendor_lead_time(vendor_id: str) -> str:
    """Retrieve replenishment fulfillment lead time and category specialization for a commercial vendor.

    Args:
        vendor_id: The supplier vendor identifier (e.g., 'VENDOR-AMUL-DIRECT')

    Returns:
        JSON string containing vendor ID, merchandise category, and delivery lead time in days.
    """
    clean_vendor_id = vendor_id.strip().upper()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT vendor_id, category, lead_time_days
            FROM vendor_lead_times
            WHERE UPPER(vendor_id) = ?;
            """,
            (clean_vendor_id,),
        )
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return json.dumps(
                {
                    "error": "VendorNotFound",
                    "vendor_id": vendor_id,
                    "message": f"No supplier record found for Vendor ID '{vendor_id}'.",
                },
                indent=2,
            )

        lead_days = row["lead_time_days"]
        sla_urgency = "RAPID_DISPATCH" if lead_days <= 2 else "STANDARD_DISPATCH"

        return json.dumps(
            {
                "vendor_id": row["vendor_id"],
                "category": row["category"],
                "lead_time_days": lead_days,
                "dispatch_sla": sla_urgency,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"error": "DatabaseQueryError", "details": str(e)},
            indent=2,
        )


if __name__ == "__main__":
    # Ensure database is present before running
    if not os.path.exists(DB_PATH):
        from database_setup import initialize_database
        initialize_database()

    # Start the FastMCP stdio server loop
    mcp.run(transport="stdio")
