#!/usr/bin/env python3
"""Tests for check-fetch-call-identity.py.

The checker is the only thing standing between the call-identity contract and a
stamp that drifts out of its output's task, so it is tested against both shapes
that defeat the contract as well as the shape that honours it.

Usage: test_check_fetch_call_identity.py
"""
import importlib.util
import os
import tempfile
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = importlib.util.spec_from_file_location(
    "check_fetch_call_identity",
    os.path.join(HERE, "check-fetch-call-identity.py"),
)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class CallIdentityCheckerTest(unittest.TestCase):
    def scan(self, **files):
        """Scan a throwaway tree holding `files` as tasks/<name>.yml."""
        with tempfile.TemporaryDirectory() as root:
            tasks = os.path.join(root, "tasks")
            os.makedirs(tasks)
            for name, body in files.items():
                with open(os.path.join(tasks, f"{name}.yml"), "w") as handle:
                    handle.write(textwrap.dedent(body).lstrip())
            return checker.scan(root)

    STAMPED_WITH_OUTPUT = """
        ---
        - name: Resolve the tag
          ansible.builtin.set_fact:
            fetched_github_tag: "v1.0.0"
            fetched_for: "{{ fetch_call_id }}"
        """

    STAMP_IN_ITS_OWN_TASK = """
        ---
        - name: Resolve the tag
          ansible.builtin.set_fact:
            fetched_github_tag: "v1.0.0"
          when: false

        - name: Mark whose fetch these outputs belong to
          ansible.builtin.set_fact:
            fetched_for: "{{ fetch_call_id }}"
        """

    NO_STAMP = """
        ---
        - name: Resolve the tag
          ansible.builtin.set_fact:
            fetched_github_tag: "v1.0.0"
        """

    def test_accepts_a_stamp_beside_its_output(self):
        self.assertEqual(self.scan(**{"fetch-good": self.STAMPED_WITH_OUTPUT}), [])

    def test_rejects_a_stamp_in_its_own_task(self):
        findings = self.scan(**{"fetch-separate": self.STAMP_IN_ITS_OWN_TASK})
        self.assertEqual(len(findings), 1)
        self.assertIn("writes no output of its own", findings[0][1])

    def test_rejects_a_file_that_never_stamps(self):
        findings = self.scan(**{"fetch-bare": self.NO_STAMP})
        self.assertEqual(len(findings), 1)
        self.assertIn("writes no fetched_for stamp at all", findings[0][1])

    def test_accepts_a_short_form_set_fact(self):
        findings = self.scan(**{"fetch-short": """
            ---
            - name: Resolve the tag
              set_fact:
                fetched_github_tag: "v1.0.0"
                fetched_for: "{{ fetch_call_id }}"
            """})
        self.assertEqual(findings, [])

    def test_accepts_a_stamp_beside_a_secondary_output(self):
        findings = self.scan(**{"fetch-multi": """
            ---
            - name: Resolve the intermediate value
              ansible.builtin.set_fact:
                _not_an_output: "x"

            - name: Resolve both outputs
              ansible.builtin.set_fact:
                fetched_flutter_version: "1.2.3"
                fetched_flutter_sha256: "deadbeef"
                fetched_for: "{{ fetch_call_id }}"
            """})
        self.assertEqual(findings, [])

    def test_ignores_the_caller_that_asserts_the_stamp(self):
        self.assertEqual(self.scan(**{"fetch-tool": self.NO_STAMP}), [])

    def test_ignores_a_file_that_is_not_a_fetch_producer(self):
        self.assertEqual(self.scan(**{"write-pins": self.NO_STAMP}), [])

    def test_reports_every_offending_file(self):
        findings = self.scan(**{
            "fetch-bare": self.NO_STAMP,
            "fetch-separate": self.STAMP_IN_ITS_OWN_TASK,
            "fetch-good": self.STAMPED_WITH_OUTPUT,
        })
        self.assertEqual(len(findings), 2)

    BORROWS_WITHOUT_ASSERTING = """
        ---
        - name: Fetch the tag from another producer
          ansible.builtin.include_tasks: fetch-github-release.yml

        - name: Strip the prefix
          ansible.builtin.set_fact:
            fetched_thing_version: "{{ fetched_github_tag | regex_replace('^v', '') }}"
            fetched_for: "{{ fetch_call_id }}"
        """

    def test_rejects_borrowing_another_fetch_output_without_asserting(self):
        findings = self.scan(**{"fetch-composed": self.BORROWS_WITHOUT_ASSERTING})
        self.assertEqual(len(findings), 1)
        self.assertIn("reads fetched_github_tag from another fetch", findings[0][1])

    def test_accepts_borrowing_when_the_file_asserts_the_stamp(self):
        asserted = self.BORROWS_WITHOUT_ASSERTING.replace(
            "- name: Strip the prefix",
            """- name: Assert the borrowed tag is this call's
          ansible.builtin.assert:
            that: fetched_for == fetch_call_id

        - name: Strip the prefix""")
        self.assertEqual(self.scan(**{"fetch-composed": asserted}), [])

    def test_reading_a_fact_the_same_file_wrote_is_not_borrowing(self):
        findings = self.scan(**{"fetch-two-stage": """
            ---
            - name: Resolve the build number
              ansible.builtin.set_fact:
                fetched_android_build: "12345"

            - name: Resolve the digest from it
              ansible.builtin.set_fact:
                fetched_android_sha1: "sha-{{ fetched_android_build }}"
                fetched_for: "{{ fetch_call_id }}"
            """})
        self.assertEqual(findings, [])

    def test_an_underscore_prefixed_fact_is_not_an_output(self):
        findings = self.scan(**{"fetch-intermediate-only": """
            ---
            - name: Stamp beside an intermediate value only
              ansible.builtin.set_fact:
                _intermediate: "x"
                fetched_for: "{{ fetch_call_id }}"
            """})
        self.assertEqual(len(findings), 1)
        self.assertIn("writes no output of its own", findings[0][1])


if __name__ == "__main__":
    unittest.main()
