import pytest
from flask import Flask
from app.utils.validators import ValidationUtils

@pytest.fixture(autouse=True)
def app_context():
    app = Flask(__name__)
    with app.app_context():
        yield

def test_contains_sensitive_info_positive():
    assert ValidationUtils.contains_sensitive_info("Email me at user@example.com")

def test_contains_sensitive_info_negative():
    assert not ValidationUtils.contains_sensitive_info("Hello world")

def test_contains_harmful_interactions_positive():
    assert ValidationUtils.contains_harmful_interactions("I want to hurt myself")

def test_contains_harmful_interactions_negative():
    assert not ValidationUtils.contains_harmful_interactions("Enjoy your day")

def test_contains_disability_info_positive():
    assert ValidationUtils.contains_disability_info("I have autism and need help")

def test_contains_disability_info_negative():
    assert not ValidationUtils.contains_disability_info("Just looking for advice")
