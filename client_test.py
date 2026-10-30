"""Automated test harness verifying MCP tools and database queries."""

import json
import os
from server import get_inventory_level, get_vendor_lead_time


def test_mcp_tools():
    print("Testing get_inventory_level()...")
    res1 = get_inventory_level("SKU-AMUL-BUTTER-500G", "DARKSTORE-DELHI-SOUTH-01")
    data1 = json.loads(res1)
    assert data1["stock_level"] == 142
    assert data1["status"] == "HEALTHY"
    print("  [PASS] Healthy stock retrieval:", data1)

    # Test OOS scenario
    res_oos = get_inventory_level("SKU-NESTLE-MILKMAID-400G", "DARKSTORE-DELHI-SOUTH-01")
    data_oos = json.loads(res_oos)
    assert data_oos["stock_level"] == 0
    assert data_oos["status"] == "CRITICAL_OOS"
    print("  [PASS] Critical OOS detection:", data_oos)

    print("\nTesting get_vendor_lead_time()...")
    res2 = get_vendor_lead_time("VENDOR-AMUL-DIRECT")
    data2 = json.loads(res2)
    assert data2["lead_time_days"] == 2
    assert data2["category"] == "Dairy & Spreads"
    print("  [PASS] Vendor lead time retrieval:", data2)

    # Test Missing record
    res_missing = get_vendor_lead_time("VENDOR-NON-EXISTENT")
    data_missing = json.loads(res_missing)
    assert data_missing["error"] == "VendorNotFound"
    print("  [PASS] Missing vendor error handling:", data_missing)

    print("\n[ALL TESTS PASSED] MCP server tools correctly interface with retail_erp.db")


if __name__ == "__main__":
    test_mcp_tools()
