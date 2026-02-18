Deploy firmware to a remote panel via SSH.

## Instructions

You are deploying the scoreboard firmware to a Raspberry Pi panel.

### Step 1: Determine target panel IP

- If arguments were provided: `$ARGUMENTS` — use the first argument as the panel IP.
- Otherwise, read `PANEL_IP` from the `.env` file at the repo root.
- If neither is available, ask the user for the panel IP.

### Step 2: Ask deployment mode

Ask the user which deployment mode to use:

- **Firmware update** (default) — pull latest code from the current git branch and restart the service.
- **Full setup** — run the full fresh installation via `m1-deploy.sh`.

### Step 3a: Firmware update flow

1. Get the current local branch name: `git branch --show-current`
2. Check if the branch is pushed to remote — run `git log origin/<branch>..<branch> --oneline`. If there are unpushed commits, warn the user and ask whether to continue.
3. SSH into the panel as `root@<panel_ip>` (use `-o StrictHostKeyChecking=no`).
4. Run on the panel:
   ```
   cd /root/7c-firmware && git fetch origin && git checkout <branch> && git pull origin <branch>
   ```
5. Restart the service: `systemctl restart 7c`
6. Tail logs to confirm startup: `journalctl -u 7c -n 20 --no-pager`
7. Show the log output to the user and confirm deployment is complete.

### Step 3b: Full setup flow

Run the existing deploy script from the `install/` directory:
```
cd install && bash m1-deploy.sh m1-setup/_setup.sh <panel_ip>
```

### Important

- Always show the user what commands you are about to run on the remote panel before executing them.
- If any SSH command fails, show the error and stop — do not continue with subsequent steps.
