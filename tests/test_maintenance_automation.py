"""Maintenance automation boundaries, without accounts or hosted execution."""

from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]


def read_yaml(path):
    """Use base scalars so YAML 1.1 does not interpret GitHub's on as True."""
    return yaml.load((ROOT / path).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def test_dependency_updates_preserve_coordinated_pins():
    config = read_yaml(".github/dependabot.yml")
    assert config["version"] == "2"
    entries = {entry["package-ecosystem"]: entry for entry in config["updates"]}
    assert len(config["updates"]) == 3
    assert set(entries) == {"github-actions", "npm", "pip"}
    for entry in entries.values():
        assert entry["directory"] == "/"
        assert entry["schedule"]["interval"] == "weekly"
        assert 0 < int(entry["open-pull-requests-limit"]) <= 2
        assert len(entry["groups"]) == 1
        assert "target-branch" not in entry
    assert entries["pip"]["allow"] == [{"dependency-name": "ruff"}]
    assert entries["pip"]["groups"]["lint-tooling"]["patterns"] == ["ruff"]


def test_hacs_checks_exact_candidate_without_privileges():
    workflow = read_yaml(".github/workflows/hacs.yml")
    assert set(workflow["on"]) == {
        "push", "pull_request", "workflow_dispatch", "schedule"
    }
    assert workflow["on"]["schedule"] == [{"cron": "23 7 * * 1"}]
    assert workflow["permissions"] == {"contents": "read"}
    for job in workflow["jobs"].values():
        assert "permissions" not in job
        assert 0 < int(job["timeout-minutes"]) <= 10
        for step in job["steps"]:
            assert "run" not in step
            assert re.fullmatch(r"hacs/action@[0-9a-f]{40}", step["uses"])
            assert step["with"] == {
                "category": "integration", "comment": "false", "ignore": "brands"
            }
            assert step["env"] == {
                "REPOSITORY_REF": "${{ github.event.pull_request.head.sha || github.sha }}"
            }
            assert "continue-on-error" not in step
        assert "continue-on-error" not in job


def test_maintenance_does_not_add_publication_or_privileged_workflows():
    """Guard the entire workflow surface against an accidental bot bypass."""
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        source = path.read_text(encoding="utf-8")
        workflow = read_yaml(path)
        assert "pull_request_target" not in workflow["on"]
        assert workflow["permissions"] == {"contents": "read"}
        assert "secrets." not in source
        assert "gh release" not in source
        assert "git push" not in source
        assert "enable-pull-request-automerge" not in source


def test_documented_workflow_names_match_configuration():
    docs = (ROOT / "docs/MAINTAINING.md").read_text(encoding="utf-8")
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        assert f'--workflow "{read_yaml(path)["name"]}"' in docs
