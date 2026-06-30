# src/pii/detector.py
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider


def build_vietnamese_analyzer() -> AnalyzerEngine:
    """Xây dựng AnalyzerEngine với các recognizer tùy chỉnh cho VN."""

    # TASK 2.2.1 — CCCD: đúng 12 chữ số
    cccd_pattern = Pattern(
        name="cccd_pattern",
        regex=r"\b\d{12}\b",
        score=0.9
    )
    cccd_recognizer = PatternRecognizer(
        supported_entity="VN_CCCD",
        supported_language="vi",
        patterns=[cccd_pattern],
        context=["cccd", "căn cước", "chứng minh", "cmnd"]
    )

    # TASK 2.2.2 — Số điện thoại VN (0[3|5|7|8|9]xxxxxxxx)
    phone_recognizer = PatternRecognizer(
        supported_entity="VN_PHONE",
        supported_language="vi",
        patterns=[Pattern(
            name="vn_phone",
            regex=r"\b0[35789]\d{8}\b",
            score=0.85
        )],
        context=["điện thoại", "sdt", "phone", "liên hệ"]
    )

    # Email recognizer cho tiếng Việt
    email_recognizer = PatternRecognizer(
        supported_entity="EMAIL_ADDRESS",
        supported_language="vi",
        patterns=[Pattern(
            name="email_pattern",
            regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            score=0.9
        )],
        context=["email", "thư", "mail", "địa chỉ"]
    )

    # PERSON pattern cho tên tiếng Việt (2-4 từ viết hoa)
    # Tên VN từ Faker("vi_VN"): "Nguyễn Thị Lan", "Trần Văn Đức", v.v.
    person_recognizer = PatternRecognizer(
        supported_entity="PERSON",
        supported_language="vi",
        patterns=[Pattern(
            name="vn_person_pattern",
            regex=r"[A-Z]\w+(?:\s[A-Z]\w+){1,3}",
            score=0.7
        )],
        context=["bệnh nhân", "họ tên", "tên", "bác sĩ"]
    )

    # TASK 2.2.3 — NLP engine (dùng vi_core_news_lg nếu có, fallback en_core_web_sm)
    import spacy
    model_name = "vi_core_news_lg" if spacy.util.is_package("vi_core_news_lg") else "en_core_web_sm"
    provider = NlpEngineProvider(nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "vi", "model_name": model_name}]
    })
    nlp_engine = provider.create_engine()

    # TASK 2.2.4 — Khởi tạo AnalyzerEngine và add recognizers
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["vi"])
    analyzer.registry.add_recognizer(cccd_recognizer)
    analyzer.registry.add_recognizer(phone_recognizer)
    analyzer.registry.add_recognizer(email_recognizer)
    analyzer.registry.add_recognizer(person_recognizer)

    return analyzer


def detect_pii(text: str, analyzer: AnalyzerEngine) -> list:
    """Detect PII trong text tiếng Việt."""
    results = analyzer.analyze(
        text=text,
        language="vi",
        entities=["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"]
    )
    return results
