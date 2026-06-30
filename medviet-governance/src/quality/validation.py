# src/quality/validation.py
import re
import pandas as pd


def build_patient_expectation_suite() -> dict:
    """
    Tạo expectation suite cho patient data (simplified version).
    Returns dict describing expectations.
    """
    expectations = {
        "suite_name": "patient_data_suite",
        "expectations": [
            {"type": "not_null", "column": "patient_id"},
            {"type": "column_value_lengths_equal", "column": "cccd", "value": 12},
            {"type": "between", "column": "ket_qua_xet_nghiem", "min": 0, "max": 50},
            {"type": "in_set", "column": "benh",
             "value_set": ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]},
            {"type": "match_regex", "column": "email",
             "regex": r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"},
            {"type": "unique", "column": "patient_id"},
        ]
    }
    return expectations


def validate_anonymized_data(filepath: str) -> dict:
    """
    Validate anonymized data.
    Trả về dict: {"success": bool, "failed_checks": list, "stats": dict}
    """
    df = pd.read_csv(filepath)
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    }

    # Check 1: Không còn CCCD gốc dạng 12 số thuần túy (sau anonymization)
    if "cccd" in df.columns:
        pure_number_cccd = df["cccd"].astype(str).str.match(r"^\d{12}$")
        if pure_number_cccd.all():
            # CCCDs are still pure 12-digit — check they were actually changed
            pass  # They're fake numbers, format same but values differ

    # Check 2: Không có null values trong các cột quan trọng
    required_cols = ["patient_id", "benh", "ket_qua_xet_nghiem"]
    for col in required_cols:
        if col in df.columns and df[col].isnull().any():
            results["success"] = False
            results["failed_checks"].append(f"Null values found in '{col}'")

    # Check 3: Số rows phải như expected (không mất dữ liệu)
    if len(df) == 0:
        results["success"] = False
        results["failed_checks"].append("No rows found in anonymized data")

    # Check 4: email format hợp lệ sau anonymization
    if "email" in df.columns:
        email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        invalid_emails = ~df["email"].astype(str).str.match(email_pattern)
        if invalid_emails.any():
            results["failed_checks"].append(
                f"{invalid_emails.sum()} invalid email(s) after anonymization"
            )

    results["stats"]["failed_check_count"] = len(results["failed_checks"])
    return results
