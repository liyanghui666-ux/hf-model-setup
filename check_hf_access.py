#!/usr/bin/env python3
"""Diagnose Hugging Face gated-repo access step by step.

A gated repo returns 403 whether the token is missing, invalid, or
simply not approved for that repo. This walks the chain and reports
which link is broken.
"""

import os
import sys

try:
    from huggingface_hub import HfApi, hf_hub_download
    from huggingface_hub.utils import (
        GatedRepoError,
        RepositoryNotFoundError,
        HfHubHTTPError,
    )
except ImportError:
    sys.exit("huggingface_hub not installed. Run: pip install huggingface_hub")


PROBE_FILES = ["config.json", "tokenizer.json"]


def ok(msg):
    print(f"[ok]   {msg}")


def fail(msg, fix=None):
    print(f"[fail] {msg}")
    if fix:
        print(f"       -> {fix}")
    sys.exit(1)


def find_token():
    for var in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN"):
        token = os.environ.get(var)
        if token:
            return token, var
    return None, None


def main(repo_id):
    token, source = find_token()
    if not token:
        fail(
            "no token in environment",
            'export HF_TOKEN="hf_..." in the shell that runs your training job',
        )
    ok(f"token found (env: {source})")

    api = HfApi(token=token)

    try:
        user = api.whoami()
    except HfHubHTTPError:
        fail(
            "token rejected by the Hub",
            "the token was revoked or mistyped; create a new one at "
            "huggingface.co/settings/tokens",
        )
    ok(f"authenticated as: {user['name']}")

    try:
        api.model_info(repo_id)
    except GatedRepoError:
        fail(
            f"account '{user['name']}' is not approved for {repo_id}",
            f"request access at huggingface.co/{repo_id} — approval is "
            "granted per account, and a fine-grained token also needs the "
            "'Read access to contents of all public gated repos' scope",
        )
    except RepositoryNotFoundError:
        fail(f"repo not found: {repo_id}", "check the spelling of the repo id")
    ok(f"gated access granted: {repo_id}")

    for filename in PROBE_FILES:
        try:
            hf_hub_download(repo_id, filename, token=token)
        except HfHubHTTPError as err:
            fail(f"{filename:<20} unreachable ({err.response.status_code})")
        ok(f"{filename:<20} reachable")

    print("\nAll checks passed. Training jobs on this machine can load "
          f"{repo_id}.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"usage: {sys.argv[0]} <repo_id>")
    main(sys.argv[1])
