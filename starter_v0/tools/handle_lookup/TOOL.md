---
name: handle_lookup
track: bonus
kind: read
requires_env: []
inputs: [display_name]
outputs: [display_name, handle, found]
side_effect: false
---
# handle_lookup

Resolves a display name (e.g. "Bill Gates") to a canonical Twitter/X handle
using a maintained internal directory. Returns `found=false` and `handle=null`
when the name is not in the directory, so the caller must fall back to
`clarify` instead of inventing a handle.
