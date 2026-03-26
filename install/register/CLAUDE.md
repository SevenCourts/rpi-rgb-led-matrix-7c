# Panel ID Registration Tool

Discovers Raspberry Pis on the local network, derives their Panel IDs, prints label strips on a Brother P-Touch 2730, and registers panels in the SevenCourts Devices Google Spreadsheet.

## Files

| File | Description |
|---|---|
| `panel-id-register.sh` | Main script — network discovery, label printing, Sheets registration |
| `panel-id-label.py` | Generates label strip PNG (QR codes + panel IDs, Montserrat font) |
| `panel-id-sheets.py` | Google Sheets API helper (appends panel to Devices worksheet) |
| `Montserrat-Regular.ttf` | Font bundled for label generation |
| `google-credentials.json` | Google service account key (**gitignored**, see below) |

## Label Strip Layout

```
[WiFi setup: iOS <QR> Android <QR>]  [panel_id × 2 small]  [panel_id × 4 large]
```

- QR codes link to SevenCourts Admin app (iOS App Store / Google Play)
- Small labels (64px): for Raspberry Pi board and packaging
- Large labels (82px): for casing
- Font: Montserrat Regular, vertically centered on 12mm tape (76px height)

## Usage

```bash
./panel-id-register.sh              # scan network, discover Pis, select, register
./panel-id-register.sh 192.168.1.42 # single device by IP
./panel-id-register.sh --dry-run    # test without printing or writing to Sheets
./panel-id-register.sh --headless   # non-interactive, auto-selects all NEW panels
```

## Prerequisites

### Hardware

- **Brother P-Touch 2730** label printer with 12mm TZe tape, connected via USB
- **Raspberry Pi(s)** with firmware SD card, connected to same LAN via ethernet
  (direct or via USB ethernet adapter)

### Software (Linux)

```bash
# 1. Build and install ptouch-print (Brother P-Touch CLI)
sudo apt-get install -y autopoint autoconf automake libtool gettext \
                        cmake libusb-1.0-0-dev libgd-dev
git clone https://github.com/torbenwendt/ptouch-print.git
cd ptouch-print
./autogen.sh && ./configure && make && sudo make install

# Verify:
ptouch-print --info   # should show PT-2730

# 2. Install Python dependencies
pip3 install gspread qrcode Pillow
# On newer systems (PEP 668):
pip3 install --break-system-packages gspread qrcode Pillow

# 3. USB permissions (one-time)
sudo sh -c 'echo "SUBSYSTEM==\"usb\", ATTR{idVendor}==\"04f9\", ATTR{idProduct}==\"2041\", MODE=\"0666\"" > /etc/udev/rules.d/99-ptouch.rules'
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### Software (Mac)

```bash
# 1. Build and install ptouch-print
brew install autoconf automake libtool gettext cmake libusb libgd
git clone https://github.com/torbenwendt/ptouch-print.git
cd ptouch-print
./autogen.sh && ./configure && make && sudo make install

# 2. Install Python dependencies
pip3 install gspread qrcode Pillow
```

### Google Sheets Service Account (`google-credentials.json`)

The file `google-credentials.json` is a Google Cloud service account key that grants
write access to the SevenCourts Devices spreadsheet. It is **gitignored** because it
contains secrets — each workstation needs its own copy.

The file looks like this:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n",
  "client_email": "sevencourts-registry@your-project-id.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

**To create it:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select existing)
3. Enable the **Google Sheets API**
4. Go to **IAM & Admin** > **Service Accounts** > **Create Service Account**
   - Name: `sevencourts-registry` (or similar)
5. Click on the service account > **Keys** > **Add Key** > **Create new key** > **JSON**
6. Save the downloaded file as `install/register/google-credentials.json`
7. Open the SevenCourts Devices spreadsheet
8. Click **Share** and add the service account email (`client_email` from the JSON) with **Editor** access

**Troubleshooting:**

If service account key creation is blocked by an org policy (`iam.disableServiceAccountKeyCreation`), disable it:
```bash
gcloud resource-manager org-policies disable-enforce iam.disableServiceAccountKeyCreation --project=YOUR_PROJECT_ID
```
This requires the **Organization Policy Administrator** role.

### SSH Access

The firmware SD card must have SSH enabled and the workstation's public key in `/root/.ssh/authorized_keys`. This is handled by the reference SD card image (keys are in `install/m1-setup/7c-vpn/ssh/authorized_keys`).

To add your key to an existing Pi manually:
```bash
cat ~/.ssh/id_ed25519.pub | ssh user@<PI_IP> "sudo sh -c 'cat >> /root/.ssh/authorized_keys'"
```

## How It Works

1. **Discovery**: Parallel SSH port scan of the local /24 subnet, then verifies each host is a Raspberry Pi by checking for `/sys/firmware/devicetree/base/serial-number`
2. **Panel ID**: Derived from the Pi's hardware serial number (same logic as `7c-set-hostname.sh`: last 8 bytes of the serial)
3. **Label generation**: Python script creates a 1-bit PNG image with QR codes and panel IDs using Pillow, printed via `ptouch-print --image`
4. **Registration**: Appends a row to the Devices Google Spreadsheet with Panel ID, Assembly Date, default location, and copies formatting (checkboxes) from the previous row

## Spreadsheet Details

- **Spreadsheet**: SevenCourts Devices
- **Worksheet**: `Devices`
- **Key columns**: `Hostname\n(Panel ID)` (col A), `Assembly Date` (col B), `Current\nLocation` (set to "Stuttgart, DE")
- **Duplicate detection**: Skips panels already registered
- **Row initialization**: Copies columns C:W from the previous row (preserves checkbox formatting), then resets values
