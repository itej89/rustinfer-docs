---
title: "Tokenizers v0.23.3 requirements"
navtitle: Requirements
section: Standards
group: "Model formats / Tokenizers v0.23.3"
order: 31
summary: What tokenizer.json holds and how Tokenizers encodes and decodes with it, and how Transformers renders a chat template.
---

# Tokenizers v0.23.3 requirements

Source: Tokenizers v0.23.3 source (local copies
`specs/model-formats/tokenizers-v0.23.3-*`, paths under `tokenizers/src/`),
and Transformers v5.23.0 `utils/chat_template_utils.py`. Defined by code;
items cite file and line. Release per item is from the SRS.

## `tokenizer.json` (R2)

| id | requirement | source |
|---|---|---|
| TOK-R1 | `tokenizer.json` is a JSON object with `version` (`"1.0"`), `truncation`, `padding`, `added_tokens`, `normalizer`, `pre_tokenizer`, `post_processor`, `decoder` and `model`. | `tokenizer/serialization.rs:13, 30-44` |
| TOK-R2 | Each `added_tokens` entry is `id` plus `content`, `single_word`, `lstrip`, `rstrip`, `normalized`, `special`. | `tokenizer/added_vocabulary.rs:17-29, 574-580` |
| TOK-R3 | `model` is one of `BPE`, `WordPiece`, `WordLevel`, `Unigram`; a `BPE` model carries `dropout`, `unk_token`, `continuing_subword_prefix`, `end_of_word_suffix`, `fuse_unk`, `byte_fallback`, `ignore_merges`, `vocab` and `merges` (in rank order). | `models/mod.rs:62-69`; `models/bpe/serialization.rs:17-40` |
| TOK-R4 | Encoding a sequence: added tokens are extracted first and the rest normalized (`extract_and_normalize`), then pre-tokenized, then tokenized by the model; the post-processor then adds special tokens when asked. | `tokenizer/mod.rs:745-787, 1236` |
| TOK-R5 | Decoding ids: each id maps to an added token or a model token, special tokens are dropped when `skip_special_tokens` is set, and the decoder joins them (or a space join without one). | `tokenizer/mod.rs:917-935` |

## Chat templates (R3)

| id | requirement | source |
|---|---|---|
| TOK-R6 | A chat template is rendered as Jinja in an `ImmutableSandboxedEnvironment` with `trim_blocks` and `lstrip_blocks`, the `loopcontrols` extension, a `tojson` filter that does not escape HTML, and the globals `raise_exception` and `strftime_now`; `add_generation_prompt` is passed to the template. | `utils/chat_template_utils.py:543-560, 620-670` |
