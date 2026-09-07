# hf-model-setup

Small utility for setting up gated Hugging Face models in local
training environments.

Working with gated repositories (Llama, Gemma, Mistral) involves a few
failure modes that all surface as the same opaque `403`. This script
separates them so you know which one you actually hit.

## What it checks

1. **Token present** — is `HF_TOKEN` exported in the current shell
2. **Token valid** — does it resolve to a real account
3. **Repo authorized** — has that account been granted access to the
   gated repo
4. **Files reachable** — can `config.json` and the tokenizer actually
   be fetched

Most "it worked yesterday" reports turn out to be step 3 (access
revoked) or a fine-grained token missing the
`Read access to contents of all public gated repos` scope.

## Usage

```bash
export HF_TOKEN="hf_..."
python check_hf_access.py meta-llama/Llama-3.2-1B
```

Output:

```
[ok]   token found (env: HF_TOKEN)
[ok]   authenticated as: your-username
[ok]   gated access granted: meta-llama/Llama-3.2-1B
[ok]   config.json         reachable
[ok]   tokenizer.json      reachable
```

Any failing step prints the specific cause and what to change, rather
than the generic HTTP error.

## Install

```bash
pip install huggingface_hub
```

## Notes

Gated access on the Hub is granted **per account**, not per machine.
A token only works if the account behind it was approved for that
repository. Copying a working token between people does not transfer
the grant — and shouldn't be done anyway.

## License

MIT
