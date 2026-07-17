from __future__ import annotations

from ai_code_stack.inventory import build_skill_inventory


def test_deterministic_rebuild(repo_root):
    first = build_skill_inventory(repo_root)
    second = build_skill_inventory(repo_root)
    names_first = sorted(row["active_name"] for row in first["skills"])
    names_second = sorted(row["active_name"] for row in second["skills"])
    assert names_first == names_second
    assert first["records"] == second["records"]


def test_no_duplicate_active_names(repo_root):
    inventory = build_skill_inventory(repo_root)
    assert inventory["duplicates"] == []
    names = [row["active_name"] for row in inventory["skills"]]
    assert len(names) == len(set(names))


def test_alias_routing_benchmark(repo_root):
    inventory = build_skill_inventory(repo_root)
    ecc_benchmark = [row for row in inventory["skills"] if row["active_name"] == "benchmark" and row["repository"] == "ecc"]
    gstack_benchmark = [row for row in inventory["skills"] if row["active_name"] == "gstack-benchmark" and row["repository"] == "gstack"]
    assert len(ecc_benchmark) == 1
    assert len(gstack_benchmark) == 1


def test_every_skill_has_required_metadata_fields(repo_root):
    inventory = build_skill_inventory(repo_root)
    required = {"active_name", "vendor_name", "repository", "source_path", "skill_file", "frontmatter", "sha256", "activation"}
    for row in inventory["skills"]:
        assert required <= set(row.keys())
        assert row["frontmatter"]["name"]
