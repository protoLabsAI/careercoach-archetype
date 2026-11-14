#!/usr/bin/env python3
"""Contract tests for the Career Coach archetype bundle manifest + README.

These lock the browser-fill default this bundle ships (careercoach-plugin#127,
task-59): NEW agents from this bundle enable Greenhouse and Ashby browser fill,
while the careercoach plugin's own manifest default stays off. The behavioural
proof that the tools actually bind lives in scripts/verify_bundle.py (the
verify-bundle workflow); this file guards the manifest/README text so a later
edit can't silently drop the default or re-assert "browser fill stays off".

Self-contained: stdlib unittest + PyYAML only, no protoAgent checkout needed.

    python3 -m unittest discover -s tests
"""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO / "protoagent.bundle.yaml"
README_PATH = REPO / "README.md"


class BundleManifestConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.raw = MANIFEST_PATH.read_text()
        self.doc = yaml.safe_load(self.raw)

    def test_config_block_seeds_greenhouse_and_ashby(self) -> None:
        # r1: top-level config: block, section key `careercoach` (the plugin's
        # config_section), browser_fill exactly "greenhouse,ashby".
        config = self.doc.get("config")
        self.assertIsInstance(config, dict, "manifest needs a top-level config: block")
        self.assertIn("careercoach", config, "config: must key on the plugin's config_section")
        self.assertEqual(config["careercoach"].get("browser_fill"), "greenhouse,ashby")

    def test_old_no_config_comment_is_gone(self) -> None:
        # r1: the "No `config:` defaults on purpose" comment must be removed.
        self.assertNotIn("No `config:` defaults on purpose", self.raw)

    def test_lever_and_workable_stay_off(self) -> None:
        # Additive guard: the default must not quietly widen past the two ATSes
        # Josh approved.
        browser_fill = self.doc["config"]["careercoach"]["browser_fill"]
        self.assertEqual(
            sorted(browser_fill.split(",")),
            ["ashby", "greenhouse"],
        )

    def test_requires_tools_includes_plan_fill(self) -> None:
        # r2: careercoach_plan_fill joins the existing three so verify proves the
        # browser-fill tools bind under the seeded default.
        requires = self.doc["archetype"]["requires_tools"]
        for tool in (
            "careercoach_find_roles",
            "careercoach_save_apply_kit",
            "browser_pdf",
            "careercoach_plan_fill",
        ):
            self.assertIn(tool, requires)

    def test_plugin_pin_unchanged(self) -> None:
        # The card forbids moving the pin or verified_against.
        careercoach = next(p for p in self.doc["plugins"] if p.get("id") == "careercoach")
        self.assertEqual(careercoach["ref"], "v0.13.4")
        self.assertEqual(str(self.doc["verified_against"]), "0.224.0")

    def test_header_comment_reflects_default_on(self) -> None:
        # The header no longer calls browser fill a default-off opt-in beta.
        self.assertNotIn("opt-in beta, default off", self.raw)
        self.assertIn("on for Greenhouse and Ashby by default", self.raw)


class ReadmeCopy(unittest.TestCase):
    def setUp(self) -> None:
        self.text = README_PATH.read_text()

    def test_no_browser_fill_stays_off_claims(self) -> None:
        # r4: none of the stale "stays off" / "default off" / "opt-in beta" lines
        # may survive.
        for stale in ("stays off", "default off", "opt-in beta"):
            self.assertNotIn(stale, self.text, f"README still claims browser fill {stale!r}")

    def test_states_greenhouse_ashby_on_by_default(self) -> None:
        self.assertIn("Greenhouse and Ashby", self.text)
        self.assertIn("browser_fill", self.text)

    def test_states_submits_need_approval(self) -> None:
        self.assertIn("submit gate", self.text)

    def test_requires_tools_example_matches_manifest(self) -> None:
        # The API example's requires_tools should list the same contract.
        self.assertIn("careercoach_plan_fill", self.text)


if __name__ == "__main__":
    unittest.main()
