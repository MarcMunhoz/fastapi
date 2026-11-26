# Repository guidance

## Shell commands

Prefix shell commands with `rtk`. Use `rtk proxy <command>` when the command needs unfiltered output, such as OpenSpec JSON.

```bash
rtk git status
rtk proxy openspec list --json
rtk docker compose exec fastapi poetry run pytest
```

Run application builds, Poetry commands, and application checks in the project container.

## OpenSpec

Use the five workflows in `.agents/skills/` and the project context in `openspec/config.yaml`. Read the main specifications under `openspec/specs/` before proposing or implementing changes that affect them.

The change lifecycle is propose → apply → sync → archive. Exploration is optional. Run each phase when requested. Keep change artifacts focused on implementation and validation.

Use the repository archive skill to archive changes. Synchronize every applicable delta spec and verify its effects in the main specs before moving the change. If the comparison or sync fails, leave the change active. Changes without delta specs can proceed after confirming that there are none.
