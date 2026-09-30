from sqlalchemy.orm import Session

from . import models


UNKNOWN_RESPONSE = (
    "I can help with scholarship eligibility, scholarships, documents, "
    "application status, payments and statistics."
)
SUPPORTED_DOCUMENT_TYPES = ("caste", "income", "domicile")


def detect_intent(message: str) -> str:
    normalized = message.casefold()

    intent_keywords = (
        (
            "STATISTICS",
            ("beneficiar", "statistics", "stats", "लाभार्थी", "आंकड़े", "आँकड़े"),
        ),
        (
            "DISBURSEMENT",
            (
                "payment", "pay", "disbursement", "भुगतान", "पैसा", "पैसे",
                "किस्त", "कब मिलेगा", "कब आएगा",
            ),
        ),
        (
            "REQUIRED_DOCUMENTS",
            (
                "document", "paperwork", "certificate", "दस्तावेज", "दस्तावेज़",
                "कागजात", "प्रमाणपत्र",
            ),
        ),
        (
            "APPLICATION_STATUS",
            (
                "application status", "status", "आवेदन की स्थिति", "आवेदन स्थिति",
                "आवेदन का स्टेटस", "स्टेटस",
            ),
        ),
        (
            "CHECK_ELIGIBILITY",
            ("eligible", "eligibility", "qualify", "पात्रता", "पात्र", "योग्य"),
        ),
        (
            "LIST_SCHOLARSHIPS",
            (
                "scholarship", "available", "छात्रवृत्ति", "स्कॉलरशिप", "कौन सी",
                "कौन-सी", "कौनसी",
            ),
        ),
    )
    for intent, keywords in intent_keywords:
        if any(keyword in normalized for keyword in keywords):
            return intent
    return "UNKNOWN"


def _is_hindi(message: str) -> bool:
    return any("\u0900" <= character <= "\u097f" for character in message)


def _eligibility_response(student: models.Student, db: Session, hindi: bool) -> str:
    scholarships = db.query(models.Scholarship).all()
    configured_scholarships = [
        scholarship
        for scholarship in scholarships
        if scholarship.category
        or scholarship.max_income is not None
        or scholarship.education_level
    ]
    if not configured_scholarships:
        if hindi:
            return "JAGO में छात्रवृत्तियों के लिए पात्रता मानदंड दर्ज नहीं हैं, इसलिए पात्रता तय नहीं की जा सकती।"
        return "Eligibility can't be determined because no scholarship eligibility criteria are configured in JAGO."

    matches = []
    for scholarship in configured_scholarships:
        if scholarship.category and scholarship.category.casefold() != student.category.casefold():
            continue
        if scholarship.max_income is not None and student.income > scholarship.max_income:
            continue
        if (
            scholarship.education_level
            and scholarship.education_level.casefold() != student.education_level.casefold()
        ):
            continue
        matches.append(scholarship.name)

    if matches:
        names = ", ".join(matches)
        if hindi:
            return (
                f"JAGO में दर्ज मानदंडों के अनुसार आपकी प्रोफ़ाइल इन छात्रवृत्तियों से मेल खाती है: {names}. "
                "यह अंतिम पात्रता निर्णय नहीं है; सभी नियम डेटाबेस में उपलब्ध नहीं हैं।"
            )
        return (
            f"Based only on the criteria stored in JAGO, your profile matches: {names}. "
            "This is not a final eligibility decision; the database may not contain all scheme rules."
        )

    if hindi:
        return (
            "JAGO में दर्ज मानदंडों के आधार पर आपकी प्रोफ़ाइल से मेल खाने वाली छात्रवृत्ति नहीं मिली। "
            "यह अंतिम पात्रता निर्णय नहीं है।"
        )
    return (
        "I couldn't find a scholarship whose stored criteria match your profile. "
        "This is not a final eligibility decision."
    )


def create_chat_response(student: models.Student, message: str, db: Session) -> dict[str, str]:
    intent = detect_intent(message)
    hindi = _is_hindi(message)

    if intent == "CHECK_ELIGIBILITY":
        response = _eligibility_response(student, db, hindi)
    elif intent == "LIST_SCHOLARSHIPS":
        scholarships = db.query(models.Scholarship).order_by(models.Scholarship.name).all()
        if not scholarships:
            response = "JAGO में अभी कोई छात्रवृत्ति सूचीबद्ध नहीं है।" if hindi else "No scholarships are currently listed in JAGO."
        else:
            names = ", ".join(scholarship.name for scholarship in scholarships)
            response = f"JAGO में उपलब्ध छात्रवृत्तियाँ: {names}." if hindi else f"Scholarships in JAGO: {names}."
    elif intent == "REQUIRED_DOCUMENTS":
        document_types = ", ".join(SUPPORTED_DOCUMENT_TYPES)
        if hindi:
            response = (
                f"JAGO में अपलोड के लिए ये दस्तावेज़ प्रकार उपलब्ध हैं: {document_types}. "
                "किसी छात्रवृत्ति के अनिवार्य दस्तावेज़ अलग से कॉन्फ़िगर नहीं हैं।"
            )
        else:
            response = (
                f"JAGO accepts these document upload types: {document_types}. "
                "Required documents are not configured per scholarship."
            )
    elif intent == "APPLICATION_STATUS":
        response = "JAGO में आवेदन की स्थिति का डेटा उपलब्ध नहीं है।" if hindi else "Application status data is not available in JAGO."
    elif intent == "DISBURSEMENT":
        response = "JAGO में भुगतान या वितरण की जानकारी उपलब्ध नहीं है।" if hindi else "Payment and disbursement data is not available in JAGO."
    elif intent == "STATISTICS":
        statistics = (
            db.query(models.ScholarshipStatistics)
            .order_by(models.ScholarshipStatistics.financial_year, models.ScholarshipStatistics.scheme)
            .all()
        )
        if not statistics:
            response = "JAGO में MoTA के आँकड़े उपलब्ध नहीं हैं।" if hindi else "MoTA statistics are not available in JAGO."
        else:
            entries = "; ".join(
                f"{row.financial_year}, {row.scheme}: {row.beneficiaries:,}"
                for row in statistics
            )
            response = f"MoTA के उपलब्ध आँकड़े (वित्त वर्ष, योजना: लाभार्थी): {entries}." if hindi else f"Available MoTA statistics (financial year, scheme: beneficiaries): {entries}."
    else:
        response = UNKNOWN_RESPONSE

    return {"intent": intent, "response": response}