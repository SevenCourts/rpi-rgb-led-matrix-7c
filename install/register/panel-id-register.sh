#!/bin/bash
# panel-id-register.sh
#
# Discovers Raspberry Pis on the local network, derives their Panel IDs,
# prints a label strip on a Brother P-Touch 2730 (12mm TZe tape) with:
#   - WiFi setup instructions + iOS/Android app QR codes
#   - 2x panel ID (small) + 4x panel ID (large)
# and registers each panel in the SevenCourts Devices Google Spreadsheet.
#
# Supports batch registration of up to 12 devices simultaneously.
#
# Usage:
#   ./panel-id-register.sh              # scan, discover, select, register
#   ./panel-id-register.sh 192.168.1.42 # single device (skip scan)
#   ./panel-id-register.sh --dry-run    # skip printing and sheets (for testing)
#
# ─── PREREQUISITES ────────────────────────────────────────────────────────────
#
# Hardware:
#   - Brother P-Touch 2730 label printer (12mm TZe tape) connected via USB
#   - Raspberry Pi(s) with firmware SD card, connected to same LAN via ethernet
#
# Software:
#   - ssh (pre-installed on Mac/Linux)
#   - python3 + gspread library
#   - ptouch-print CLI (built from source, see below)
#
# USB permissions (Linux only, one-time):
#   sudo sh -c 'echo "SUBSYSTEM==\"usb\", ATTR{idVendor}==\"04f9\", \
#     ATTR{idProduct}==\"2041\", MODE=\"0666\"" \
#     > /etc/udev/rules.d/99-ptouch.rules'
#   sudo udevadm control --reload-rules && sudo udevadm trigger
#
# ─── ONE-TIME SETUP ──────────────────────────────────────────────────────────
#
# 1. Install ptouch-print (Brother P-Touch CLI tool):
#
#      Linux:
#        sudo apt-get install -y autopoint autoconf automake libtool gettext \
#                                cmake libusb-1.0-0-dev libgd-dev
#        git clone https://github.com/torbenwendt/ptouch-print.git
#        cd ptouch-print
#        ./autogen.sh && ./configure && make && sudo make install
#
#      Mac:
#        # install Xcode command line tools, then same autotools steps as Linux
#        # (use Homebrew for dependencies: brew install autoconf automake libtool
#        #  gettext cmake libusb libgd)
#
#      Verify: ptouch-print --info  (should show PT-2730)
#
# 2. Install Python dependencies:
#      pip3 install gspread qrcode Pillow
#      (on newer systems: pip3 install --break-system-packages gspread)
#
# 3. Set up Google Sheets service account:
#      a. Go to https://console.cloud.google.com/
#      b. Create a project (or select an existing one)
#      c. Enable the "Google Sheets API" for the project
#      d. Go to "IAM & Admin" → "Service Accounts" → "Create Service Account"
#      e. Click on the service account → "Keys" → "Add Key" → "Create new key" → JSON
#      f. Save the downloaded file as: install/google-credentials.json
#      g. Open the SevenCourts Devices spreadsheet
#      h. Click "Share" and add the service account email
#         (client_email from the JSON file) with "Editor" access
#
# 4. SSH access:
#      The firmware SD card must have SSH enabled and the workstation's public
#      key in /root/.ssh/authorized_keys. This is handled by the reference SD
#      card image (see install/m1-setup/7c-vpn/ssh/authorized_keys).
#
# ───────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LABEL_SCRIPT="$SCRIPT_DIR/panel-id-label.py"
SHEETS_SCRIPT="$SCRIPT_DIR/panel-id-sheets.py"
CREDENTIALS_FILE="$SCRIPT_DIR/google-credentials.json"

SSH_USER="root"
SSH_OPTS="-o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=yes -o LogLevel=ERROR"
LABEL_COUNT=6
TAPE_WIDTH=12  # mm

MY_IP=$(hostname -I | awk '{print $1}')

DRY_RUN=false
HEADLESS=false
GIVEN_IP=""

# ─── Argument parsing ─────────────────────────────────────────────────────────

for arg in "$@"; do
    case "$arg" in
        --dry-run)   DRY_RUN=true ;;
        --headless)  HEADLESS=true ;;
        --help|-h)
            sed -n '/^# Usage:/,/^# ──/p' "$0" | head -n 5 | sed 's/^# //'
            exit 0
            ;;
        -*) echo "Unknown option: $arg" >&2; exit 1 ;;
        *)  GIVEN_IP="$arg" ;;
    esac
done

# ─── Helpers ──────────────────────────────────────────────────────────────────

info()  { echo "  $*"; }
ok()    { echo "  ✓ $*"; }
warn()  { echo "  ! $*"; }
fail()  { echo "  ✗ $*" >&2; exit 1; }
header(){ echo; echo "── $* ──"; }

check_prerequisites() {
    local missing=()

    command -v ssh       &>/dev/null || missing+=("ssh")
    command -v python3   &>/dev/null || missing+=("python3")
    command -v ptouch-print &>/dev/null || {
        if [[ "$DRY_RUN" == "false" ]]; then
            missing+=("ptouch-print  # see setup instructions at top of this script")
        fi
    }

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "Missing dependencies:" >&2
        for m in "${missing[@]}"; do echo "  - $m" >&2; done
        exit 1
    fi

    if [[ ! -f "$CREDENTIALS_FILE" && "$DRY_RUN" == "false" ]]; then
        fail "Google credentials not found at: $CREDENTIALS_FILE
  See setup instructions at the top of this script."
    fi
}

# ─── Pi discovery ─────────────────────────────────────────────────────────────

# Discover all Raspberry Pis on the local /24 subnet.
# Returns one IP per line.
discover_pis() {
    set +e  # SSH failures are expected during scanning
    local subnet
    subnet=$(echo "$MY_IP" | sed 's/\.[0-9]*$/./')

    echo "  Scanning ${subnet}0/24 for Raspberry Pis..." >&2

    # Phase 1: fast parallel port scan for SSH
    rm -f /tmp/7c-ssh-hosts.txt
    for i in $(seq 1 254); do
        local ip="${subnet}${i}"
        [[ "$ip" == "$MY_IP" ]] && continue
        ( timeout 0.5 bash -c "echo >/dev/tcp/$ip/22" 2>/dev/null && echo "$ip" >> /tmp/7c-ssh-hosts.txt ) &
    done
    wait

    if [[ ! -f /tmp/7c-ssh-hosts.txt ]]; then
        return
    fi

    # Phase 2: verify each SSH host is a Pi (has serial-number file)
    local verified_file="/tmp/7c-verified-pis.txt"
    rm -f "$verified_file"
    while IFS= read -r ip; do
        if ssh $SSH_OPTS "$SSH_USER@$ip" "test -f /sys/firmware/devicetree/base/serial-number" < /dev/null 2>/dev/null; then
            echo "$ip" >> "$verified_file"
        fi
    done < <(sort -t. -k4 -n /tmp/7c-ssh-hosts.txt)

    if [[ -f "$verified_file" ]]; then
        cat "$verified_file"
        rm -f "$verified_file"
    fi
    rm -f /tmp/7c-ssh-hosts.txt
    set -e
}

# ─── Panel ID ─────────────────────────────────────────────────────────────────

get_panel_id() {
    local ip=$1
    ssh $SSH_OPTS "$SSH_USER@$ip" \
        "cat /sys/firmware/devicetree/base/serial-number | tail -c +9 | tr -d '\0\n'" < /dev/null
}

# Check if a panel ID is already in the spreadsheet.
# Returns "registered" or "new".
check_registration() {
    local panel_id=$1
    python3 -c "
import gspread, sys
gc = gspread.service_account(filename='$CREDENTIALS_FILE')
sh = gc.open_by_key('$(python3 -c "
import sys; sys.path.insert(0, '$SCRIPT_DIR')
from importlib.machinery import SourceFileLoader
m = SourceFileLoader('sheets', '$SHEETS_SCRIPT').load_module()
print(m.SPREADSHEET_ID)
")')
ws = sh.worksheet('Devices')
col = ws.col_values(1)
print('registered' if '$panel_id' in col else 'new')
" 2>/dev/null || echo "unknown"
}

# ─── Label printing ───────────────────────────────────────────────────────────

print_label() {
    local panel_id=$1

    if [[ "$DRY_RUN" == "true" ]]; then
        info "[dry-run] Would print label: $panel_id"
        return
    fi

    local label_png="/tmp/7c-label-${panel_id}.png"
    python3 "$LABEL_SCRIPT" "$panel_id" "$label_png"
    ptouch-print --image "$label_png"
    rm -f "$label_png"
}

# ─── Google Sheets registration ───────────────────────────────────────────────

register_in_sheets() {
    local panel_id=$1
    local assembly_date
    assembly_date=$(date +%Y-%m-%d)

    if [[ "$DRY_RUN" == "true" ]]; then
        info "[dry-run] Would register: panel_id=$panel_id, date=$assembly_date"
        return
    fi

    python3 "$SHEETS_SCRIPT" "$panel_id" "$assembly_date"
}

# ─── Process a single panel ──────────────────────────────────────────────────

process_panel() {
    local ip=$1
    local panel_id=$2

    info "Processing $panel_id ($ip)..."
    print_label "$panel_id"
    ok "Label printed"
    register_in_sheets "$panel_id"
    ok "Registered in spreadsheet"
}

# ─── Interactive multi-device flow ────────────────────────────────────────────

run_batch() {
    header "Scanning for Raspberry Pis"

    # Discover all Pis
    local ips=()
    while IFS= read -r ip; do
        [[ -n "$ip" ]] && ips+=("$ip")
    done < <(discover_pis)

    if [[ ${#ips[@]} -eq 0 ]]; then
        fail "No Raspberry Pis found on local network.
  Make sure Pis are connected, booted, and SSH is accessible."
    fi

    info "Found ${#ips[@]} Raspberry Pi(s). Fetching Panel IDs..."

    # Gather panel IDs and registration status
    local panel_ids=()
    local statuses=()
    local new_indices=()

    for idx in "${!ips[@]}"; do
        local ip="${ips[$idx]}"
        local panel_id
        panel_id=$(get_panel_id "$ip" 2>/dev/null || echo "")
        panel_ids+=("$panel_id")

        if [[ -z "$panel_id" ]]; then
            statuses+=("error")
        elif [[ "$DRY_RUN" == "true" ]]; then
            statuses+=("new")
            new_indices+=($((idx + 1)))
        else
            local status
            status=$(check_registration "$panel_id")
            statuses+=("$status")
            if [[ "$status" == "new" ]]; then
                new_indices+=($((idx + 1)))
            fi
        fi
    done

    # Display table
    header "Discovered Panels"
    printf "  %-4s %-12s %-18s %s\n" "#" "Panel ID" "IP" "Status"
    printf "  %-4s %-12s %-18s %s\n" "---" "--------" "--" "------"

    for idx in "${!ips[@]}"; do
        local num=$((idx + 1))
        local status_display="${statuses[$idx]}"
        case "$status_display" in
            new)         status_display="NEW" ;;
            registered)  status_display="already registered" ;;
            error)       status_display="ERROR: could not read ID" ;;
            unknown)     status_display="could not check" ;;
        esac
        printf "  %-4s %-12s %-18s %s\n" "$num" "${panel_ids[$idx]:-???}" "${ips[$idx]}" "$status_display"
    done
    echo

    # Build default selection (NEW panels only)
    local default_selection=""
    if [[ ${#new_indices[@]} -gt 0 ]]; then
        default_selection=$(IFS=,; echo "${new_indices[*]}")
    fi

    local selection=""
    if [[ "$HEADLESS" == "true" ]]; then
        # Headless: auto-select all NEW panels
        selection="$default_selection"
        if [[ -z "$selection" ]]; then
            info "No new panels to register."; return
        fi
        info "Auto-selecting: $selection"
    elif [[ -z "$default_selection" ]]; then
        info "No new panels to register."
        read -rp "  Register anyway? Enter panel numbers (e.g. 1,3,5) or 'q' to quit: " selection
        [[ "$selection" == "q" || -z "$selection" ]] && { info "Nothing to do."; return; }
    else
        read -rp "  Register [$default_selection]: " selection
        selection="${selection:-$default_selection}"
        [[ "$selection" == "q" ]] && { info "Cancelled."; return; }
    fi

    # Parse selection
    local selected=()
    IFS=',' read -ra tokens <<< "$selection"
    for token in "${tokens[@]}"; do
        token=$(echo "$token" | tr -d ' ')
        if [[ "$token" =~ ^[0-9]+$ ]] && (( token >= 1 && token <= ${#ips[@]} )); then
            selected+=("$token")
        else
            warn "Ignoring invalid selection: $token"
        fi
    done

    if [[ ${#selected[@]} -eq 0 ]]; then
        info "No panels selected."
        return
    fi

    # Process selected panels
    header "Registering ${#selected[@]} panel(s)"
    local success=0
    for num in "${selected[@]}"; do
        local idx=$((num - 1))
        local ip="${ips[$idx]}"
        local panel_id="${panel_ids[$idx]}"

        if [[ -z "$panel_id" || "$panel_id" == "???" ]]; then
            warn "Skipping #$num — could not read Panel ID"
            continue
        fi

        process_panel "$ip" "$panel_id"
        success=$((success + 1))
    done

    header "Done — $success panel(s) registered"
    echo "  Date: $(date +%Y-%m-%d)"
    echo
    echo "  Next: attach Label #1 to each Raspberry Pi, then proceed with assembly."
}

# ─── Single-device flow ──────────────────────────────────────────────────────

run_single() {
    local ip="$GIVEN_IP"

    info "Using provided IP: $ip"

    # Wait for SSH
    local retries=20
    info "Waiting for SSH on $ip..."
    for ((i=1; i<=retries; i++)); do
        if ssh $SSH_OPTS "$SSH_USER@$ip" true < /dev/null 2>/dev/null; then
            break
        fi
        if ((i == retries)); then
            fail "SSH not available on $ip after $((retries * 3)) seconds."
        fi
        sleep 3
    done
    ok "SSH connection established"

    local panel_id
    panel_id=$(get_panel_id "$ip")
    [[ -z "$panel_id" ]] && fail "Could not read Panel ID from Pi at $ip"
    ok "Panel ID: $panel_id"

    process_panel "$ip" "$panel_id"

    header "Done"
    echo "  Panel ID : $panel_id"
    echo "  Date     : $(date +%Y-%m-%d)"
    echo
    echo "  Next: attach Label #1 to the Raspberry Pi, then proceed with assembly."
}

# ─── Main ─────────────────────────────────────────────────────────────────────

main() {
    header "SevenCourts Panel ID Registration"
    [[ "$DRY_RUN" == "true" ]] && info "(dry-run mode — no printer or spreadsheet writes)"

    check_prerequisites

    if [[ -n "$GIVEN_IP" ]]; then
        run_single
    else
        run_batch
    fi
}

main
