from __future__ import annotations

import yaml


def _load(repo_root, name):
    return yaml.safe_load((repo_root / "policies" / name).read_text(encoding="utf-8"))


def test_runtime_policy_limits(repo_root):
    runtime = _load(repo_root, "runtime.yaml")
    assert runtime["limits"]["max_skills_per_agent"] == 5
    assert runtime["limits"]["max_active_subagents"] == 3
    assert runtime["limits"]["nested_subagents"] is False
    assert runtime["limits"]["cross_platform_delegation"] is False


def test_execution_budget_task_classes_present(repo_root):
    budget = _load(repo_root, "execution-budget.yaml")
    classes = budget["task_classes"]
    assert classes["question"]["max_subagents"] == 0
    assert classes["tiny"]["max_subagents"] == 0
    assert classes["small"]["max_subagents"] == 1
    assert classes["medium"]["max_subagents"] == 2
    assert classes["large_or_risky"]["hard_limit_subagents"] == 3


def test_execution_budget_hard_limits_match_runtime(repo_root):
    budget = _load(repo_root, "execution-budget.yaml")
    runtime = _load(repo_root, "runtime.yaml")
    assert budget["defaults"]["hard_limit_skills_per_agent"] == runtime["limits"]["max_skills_per_agent"]
    assert budget["defaults"]["hard_limit_active_subagents"] == runtime["limits"]["max_active_subagents"]


def test_nested_subagents_and_delegation_disabled_everywhere(repo_root):
    budget = _load(repo_root, "execution-budget.yaml")
    assert budget["runtime_flags"]["nested_subagents"] is False
    assert budget["runtime_flags"]["cross_platform_delegation"] is False
    assert budget["runtime_flags"]["pass_full_chat_history"] is False
