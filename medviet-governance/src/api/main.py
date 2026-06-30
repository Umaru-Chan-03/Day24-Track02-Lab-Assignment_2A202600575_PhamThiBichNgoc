# src/api/main.py
import os
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from src.access.rbac import get_current_user, require_permission
from src.pii.anonymizer import MedVietAnonymizer

app = FastAPI(title="MedViet Data API", version="1.0.0")
anonymizer = MedVietAnonymizer()

_DATA_RAW = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "raw", "patients_raw.csv"
))


@app.get("/api/patients/raw")
@require_permission(resource="patient_data", action="read")
async def get_raw_patients(
    current_user: dict = Depends(get_current_user)
):
    """Trả về raw patient data — chỉ admin được phép."""
    df = pd.read_csv(_DATA_RAW)
    return JSONResponse(content=df.head(10).to_dict(orient="records"))


@app.get("/api/patients/anonymized")
@require_permission(resource="training_data", action="read")
async def get_anonymized_patients(
    current_user: dict = Depends(get_current_user)
):
    """Trả về anonymized data — ml_engineer và admin."""
    df = pd.read_csv(_DATA_RAW)
    df_anon = anonymizer.anonymize_dataframe(df.head(10))
    return JSONResponse(content=df_anon.to_dict(orient="records"))


@app.get("/api/metrics/aggregated")
@require_permission(resource="aggregated_metrics", action="read")
async def get_aggregated_metrics(
    current_user: dict = Depends(get_current_user)
):
    """Trả về aggregated metrics không có PII."""
    df = pd.read_csv(_DATA_RAW)
    metrics = df.groupby("benh").agg(
        so_luong=("patient_id", "count"),
        ket_qua_tb=("ket_qua_xet_nghiem", "mean")
    ).reset_index()
    metrics["ket_qua_tb"] = metrics["ket_qua_tb"].round(2)
    return JSONResponse(content=metrics.to_dict(orient="records"))


@app.delete("/api/patients/{patient_id}")
@require_permission(resource="patient_data", action="delete")
async def delete_patient(
    patient_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Chỉ admin được xóa. Các role khác nhận 403."""
    return JSONResponse(content={
        "message": f"Patient {patient_id} deleted",
        "deleted_by": current_user["username"]
    })


@app.get("/health")
async def health():
    return {"status": "ok", "service": "MedViet Data API"}
