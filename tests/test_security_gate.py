from __future__ import annotations

from ai_code_stack.security_gate import evaluate_release


def test_missing_report_blocks():
    outcome = evaluate_release(None, "abc123", True)
    assert outcome["status"] == "blocked"


def test_fingerprint_mismatch_blocks():
    report = {"audited_diff_sha256": "aaa", "findings": []}
    outcome = evaluate_release(report, "bbb", True)
    assert outcome["status"] == "blocked"


def test_failing_tests_block():
    report = {"audited_diff_sha256": "abc", "findings": []}
    outcome = evaluate_release(report, "abc", False)
    assert outcome["status"] == "blocked"


def test_open_critical_finding_blocks():
    report = {"audited_diff_sha256": "abc", "findings": [{"severity": "CRITICAL", "status": "open"}]}
    outcome = evaluate_release(report, "abc", True)
    assert outcome["status"] == "blocked"
    assert outcome["critical_open"] == 1


def test_open_high_finding_blocks():
    report = {"audited_diff_sha256": "abc", "findings": [{"severity": "HIGH", "status": "open"}]}
    outcome = evaluate_release(report, "abc", True)
    assert outcome["status"] == "blocked"


def test_resolved_finding_passes():
    report = {"audited_diff_sha256": "abc", "findings": [{"severity": "CRITICAL", "status": "resolved"}]}
    outcome = evaluate_release(report, "abc", True)
    assert outcome["status"] == "pass"


def test_explicitly_accepted_risk_passes():
    report = {"audited_diff_sha256": "abc", "findings": [{
        "severity": "HIGH", "status": "open", "risk_accepted": True, "approved_by": "security-lead",
    }]}
    outcome = evaluate_release(report, "abc", True)
    assert outcome["status"] == "pass"
    assert outcome["approved_risks"]


def test_risk_accepted_without_approver_still_blocks():
    report = {"audited_diff_sha256": "abc", "findings": [{
        "severity": "HIGH", "status": "open", "risk_accepted": True, "approved_by": "",
    }]}
    outcome = evaluate_release(report, "abc", True)
    assert outcome["status"] == "blocked"


def test_clean_report_passes():
    report = {"audited_diff_sha256": "abc", "findings": []}
    outcome = evaluate_release(report, "abc", True)
    assert outcome["status"] == "pass"


def test_low_and_medium_findings_never_block():
    report = {"audited_diff_sha256": "abc", "findings": [
        {"severity": "LOW", "status": "open"}, {"severity": "MEDIUM", "status": "open"},
    ]}
    outcome = evaluate_release(report, "abc", True)
    assert outcome["status"] == "pass"
