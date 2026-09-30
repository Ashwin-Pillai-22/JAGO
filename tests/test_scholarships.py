from app.chatbot import create_chat_response, detect_intent
from app.schemas import ScholarshipResponse


def test_scholarship_response_includes_application_url():
    scholarship = ScholarshipResponse(
        id=1,
        name='National Scholarship',
        scheme='National Scholarship',
        category='ST',
        education_level='Undergraduate',
        description='A sample scheme',
        application_url='https://scholarships.gov.in/'
    )

    assert scholarship.application_url == 'https://scholarships.gov.in/'


def test_chatbot_detects_deficiency_and_disbursement_queries():
    assert detect_intent('My scholarship application has a deficiency notice') == 'DEFICIENCY'
    assert detect_intent('When will the disbursement be released?') == 'DISBURSEMENT'

    response = create_chat_response(
        student=None,
        message='My application has a deficiency and when is disbursement?',
        db=None,
    )

    assert response['intent'] in {'DEFICIENCY', 'DISBURSEMENT'}
    assert 'deficiency' in response['response'].lower() or 'disbursement' in response['response'].lower()
