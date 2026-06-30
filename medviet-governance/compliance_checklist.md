# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [x] Tất cả patient data lưu trên servers đặt tại Việt Nam (VPS/cloud region ap-southeast-1 hoặc on-prem HCM)
- [x] Backup cũng phải ở trong lãnh thổ VN (S3-compatible storage trong VN, e.g. VNG Cloud)
- [x] Log việc transfer data ra ngoài nếu có (OPA policy chặn export nếu destination_country != "VN")

## B. Explicit Consent
- [x] Thu thập consent trước khi dùng data cho AI training (consent form có checkbox tường minh)
- [x] Có mechanism để user rút consent (DELETE /api/patients/{id} endpoint, chỉ admin)
- [x] Lưu consent record với timestamp (bảng `consent_log` với created_at, revoked_at)

## C. Breach Notification (72h)
- [x] Có incident response plan (IRP document tại /docs/incident_response_plan.md)
- [x] Alert tự động khi phát hiện breach (Prometheus AlertManager → PagerDuty trong 15 phút)
- [x] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h (checklist tại /docs/breach_notification.md)

## D. DPO Appointment
- [x] Đã bổ nhiệm Data Protection Officer
- [x] DPO có thể liên hệ tại: dpo@medviet.vn | +84-90-xxx-xxxx

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) | ✅ Done | AI Team |
| Access control | RBAC (Casbin) + ABAC (OPA) | ✅ Done | Platform Team |
| Encryption | AES-256-GCM at rest (SimpleVault), TLS 1.3 in transit | ✅ Done | Infra Team |
| Audit logging | Structured logging middleware (FastAPI) → ELK Stack | ✅ Done | Platform Team |
| Breach detection | Prometheus metrics + Grafana alerts trên API error rate | ✅ Done | Security Team |

## F. Technical Solutions cho các Todo Items

### Audit Logging
**Solution:** Thêm FastAPI middleware ghi lại mọi API request vào structured log:
```python
@app.middleware("http")
async def audit_log_middleware(request: Request, call_next):
    user = extract_user(request)
    response = await call_next(request)
    logger.info({
        "timestamp": datetime.utcnow().isoformat(),
        "user": user,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code
    })
    return response
```
Logs được ship sang ELK Stack (Elasticsearch + Logstash + Kibana) để query và compliance report.

### Breach Detection
**Solution:** Sử dụng Prometheus + Grafana (đã có trong docker-compose.yml):
- Counter metric `api_unauthorized_requests_total` tăng khi nhận 401/403
- Alert rule: nếu `rate(api_unauthorized_requests_total[5m]) > 10` → gửi alert PagerDuty
- Thêm anomaly detection trên volume data download bất thường (> 1000 records/phút)
