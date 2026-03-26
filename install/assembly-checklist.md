# M1 Panel Assembly Checklist

## Tools Required
- Phillips screwdriver
- RasPi tester device (HUB75 GPIO driver + special test firmware)
- SD card copying device + reference SD card *(see: "Reference SD Card Preparation")*
- Workstation with `register/panel-id-register.sh` installed (Mac or Linux)
- Brother P-Touch 2730 label printer (12mm TZe tape) connected to workstation
  - CLI tool: [ptouch-print](https://github.com/torbenwendt/ptouch-print) (build from source, see `register/panel-id-register.sh` header)

---

## Step 1 — Ordering

- [ ] Send order to CXGD via WhatsApp group
  - Typical batch size: **12 units**
  - Spec: P5 outdoor 64×32 LED panels, power unit, casing (no PCB)
- [ ] Confirm order details and expected delivery date

---

## Step 2 — Incoming Inspection

*Performed on all units before any assembly.*

- [ ] Count boxes — verify quantity matches order
- [ ] Open boxes, visually inspect each unit:
  - [ ] Casing for physical damage
  - [ ] LED panel surface for damage
  - [ ] Cables and connectors condition
- [ ] Test each panel with RasPi tester device:
  - [ ] Connect HUB75 GPIO driver to panel HUB75 connectors
  - [ ] Power on panel
  - [ ] Verify **full white screen** — all LEDs must light up uniformly
  - [ ] Verify **color rainbow gradient** — no dead zones or color errors
  - [ ] Power off and disconnect tester

**For any damaged panel — photograph all damaged parts and report to CXGD, then classify:**

| Damage Grade | Action |
|---|---|
| Negligible | Proceed to production |
| Small | Set aside for rental units |
| Significant | Request repair parts from CXGD. **Do not ship back** (return transport to China is not cost-effective). |

---

## Step 3 — SD Card Preparation

*Prepare one SD card per unit before assembly.*

- [ ] For each unit, copy reference SD card using SD card copying device
  *(see separate document: "Reference SD Card Preparation")*
- [ ] Verify each copy completed successfully

---

## Step 4 — Panel ID Extraction & Label Printing

*Performed on bare Raspberry Pi — before casing assembly — so labels are ready when needed.*

**For each Raspberry Pi in the batch:**

- [ ] Attach passive cooler set to Raspberry Pi
- [ ] Insert SD card into Raspberry Pi
- [ ] Connect Raspberry Pi to office ethernet
- [ ] Power on Raspberry Pi (USB-C power)
- [ ] Wait for boot (~60 seconds)
- [ ] On workstation, run:
  ```
  ./register/panel-id-register.sh
  ```
  The script will:
  - Auto-discover all Pis on the local network (parallel SSH port scan)
  - SSH in and derive Panel IDs from hardware serial numbers
  - Show an interactive table of discovered panels (NEW / already registered)
  - For each selected panel, print **one label strip** on the Brother P-Touch 2730:
    - WiFi setup instructions with iOS and Android app QR codes
    - 2× panel ID (small font, for Pi board and packaging)
    - 4× panel ID (large font, for casing)
  - Register Panel ID + assembly date in the Google Spreadsheet
- [ ] Verify label strips printed correctly — QR codes scannable, panel IDs legible
- [ ] Cut label strips into individual labels
- [ ] Power off Raspberry Pis and disconnect ethernet

**All units in the batch can be processed in one script run (up to 12 simultaneously).**

---

## Step 5 — Raspberry Pi Component Assembly

*Performed after labels are printed for all units in the batch.*

- [ ] Attach HUB75 GPIO driver board to Raspberry Pi GPIO pins
- [ ] Set RTC switch on driver board to **"RTC ON"** position
- [ ] Insert CR1220 battery into RTC socket on driver board
- [ ] Secure HUB75 driver board to Raspberry Pi with cable tie
- [ ] Stick **Label #1** on Raspberry Pi (any flat visible surface)

---

## Step 6 — Casing Assembly

- [ ] Connect HUB75 cables (supplied by CXGD) to **"Top"** and **"Middle"** HUB75 connectors on the panel
  *(leave "Bottom" connector empty)*
- [ ] Connect USB-C cable open end to the power unit using Phillips screwdriver

  > **⚠️ CRITICAL:** In the next step, the USB-C cable **must** be secured with a cable tie.
  > A loose USB-C cable will disconnect under vibration and brick the device.

- [ ] **Secure USB-C cable with cable tie**
- [ ] Connect external USB socket on casing to Raspberry Pi USB port
- [ ] Mount Raspberry Pi into casing using cable ties
- [ ] Insert SD card into Raspberry Pi *(if not already inserted in Step 4)*
- [ ] Stick labels on casing:
  - [ ] **Label #2** — front side, upper right corner
  - [ ] **Label #3** — top side, bottom left corner
  - [ ] **Label #4** — right side, bottom centered
- [ ] Close casing with Phillips screwdriver

---

## Step 7 — Final Test

- [ ] Connect panel to 220V power
- [ ] Connect panel to office ethernet
- [ ] Open **sevencourts.admin.ng** app and connect panel to office WiFi
  *(Future: automate WiFi provisioning)*
- [ ] Verify panel connects to SevenCourts server (status indicator turns green)
- [ ] Open **Tennis Math** app and verify scoreboard display
  *(Future: consider a simpler automated smoke test)*
- [ ] Power off panel

---

## Step 8 — Packaging

- [ ] Compact 220V cable neatly and secure with cable zip tie
- [ ] Place panel in bubble sleeve (supplied with CXGD delivery)
- [ ] Stick **Label #5** and **Label #6** on outside of packaging (Panel ID visible)

  *(Future: add QR code sticker linking to installation manual)*

- [ ] Unit is ready for shipment or storage
