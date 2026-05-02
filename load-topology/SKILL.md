---
name: load-topology
description: Read the local system topology to discover available machines and models. Use when the user wants to see what models can be run, load a model on a machine, or prepare for task delegation. Triggers on "load topology", "what models are available", "which machines are running", "start a model", "load a model on", or "show me the topology".
---

# Load Topology

This skill reads the local system topology file to enumerate available machines and models, then helps the user start a chosen model so work can be delegated via the task-tracking skill.

## Step 1 — Read the topology file

Read the full file at:

```
~/code/github/nicholasf/local-system/topology.md
```

## Step 2 — Scan the Model Startup Commands section

Locate the **Model Startup Commands** table. Extract every row and present it to the user as a numbered list in this format:

```
Available models:

  1. qwen3-coder-30b   on pond    (llama-server / CUDA,  port 9337, ~215 t/s)
  2. qwen2.5-coder-32b on pond    (llama-server / CUDA,  port 9337, ~30 t/s)
  3. qwen3-coder-30b   on gollum  (llama-server / ROCm,  port 9337, ~TBD t/s)
  4. qwen2.5-coder-32b on gollum  (llama-server / ROCm,  port 9337, ~TBD t/s)
  5. qwen2.5-coder:14b on gollum  (Ollama / ROCm,        port 11434)
  6. qwen2.5-coder:7b  on gollum  (Ollama / ROCm,        port 11434)
```

Also note which model is **currently running** (marked in the topology) and offer to skip startup if it is already active.

## Step 3 — Check what is currently running (optional but recommended)

If the user wants a live check before starting, run:

```bash
curl -s http://pond:9337/v1/models
```

or

```bash
ssh nicholasf@pond "pgrep -a llama-server"
```

Report the result so the user can confirm whether a model swap is needed.

## Step 4 — User selects a model

Ask the user which numbered entry they want to load (or confirm they want to keep the current one).

## Step 5 — Present the startup command

Look up the named anchor in the topology file that corresponds to the user's choice (e.g. `### pond — qwen3-coder-30b`) and display the full bash command block from that section.

Remind the user to kill any existing `llama-server` instance first if swapping models:

```bash
ssh nicholasf@pond "pkill -f llama-server"
# or for gollum:
ssh nicholasf@gollum "pkill -f llama-server"
```

Then show the startup command. Offer to execute it directly if the user confirms.

## Step 6 — Confirm the model is live

After starting, verify with:

```bash
curl -s http://<machine>:9337/v1/models
```

Report the model name returned. The model is ready when this returns a valid JSON response.

## Step 7 — Hand off to task-tracking

Once a model is confirmed running, inform the user:

- Which machine and model are active
- The API endpoint (e.g. `http://pond:9337`)
- That tasks can now be created and assigned to this model using the **task-tracking** skill

Suggest the user say something like:  
> "Create a task for…" — the task-tracking skill will then read `topology.md` to confirm the model assignment.

## Notes

- The topology file is the source of truth for machine names, VRAM, backends, and startup commands. Always read it fresh — do not rely on cached knowledge.
- If the topology file does not exist at the expected path, tell the user and stop.
- If the user asks about mesh-llm or multi-node tensor-split, refer them to the **mesh-llm** sections of the topology file; that is out of scope for this skill.
