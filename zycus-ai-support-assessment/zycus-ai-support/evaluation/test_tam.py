from app.tam.pipeline import generate_account_health


def test_tam_sections():
    r = generate_account_health("ACC-3336")
    assert r.executive_summary
    assert r.open_risks is not None
    assert r.talking_points


def test_tam_missing_account():
    r = generate_account_health("ACC-DOES-NOT-EXIST")
    assert r.account_found is False
    assert r.executive_summary


def test_tam_deterministic_without_llm():
    assert generate_account_health("ACC-7893").model_dump() == generate_account_health("ACC-7893").model_dump()
