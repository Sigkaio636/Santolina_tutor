# Arduino UNO Q 4 GB (ABX00173): board reference

> **What this is:** a reference for team members. Use it when you need a fact about the UNO Q: a
> spec, a pin, a port, a limit or a measured speed. To prepare the board step by step, follow
> [BOARD_SETUP.md](BOARD_SETUP.md). To deploy our copilot, follow
> [Deploy the copilot on the board](how-to/deploy-copilot-on-board.md).
>
> It condenses the store page and Arduino's official documentation (datasheet rev. 16, user
> manual, power specification, single-board computer (SBC), ADB/SSH, Debian and llama.cpp guides).
> Collected 2026-11-14.
>
> **How to read it:** most facts come from the datasheet and Arduino's guides in
> [Sources](#sources). Not every table names its source. Official docs describe the
> *hardware*. What actually runs on *our* board is in [BOARD_SETUP.md](BOARD_SETUP.md), the
> [`unoq-board` skill](https://github.com/Sigkaio636/Santolina_tutor/blob/main/.claude/skills/unoq-board/SKILL.md)
> and §14. Unsettled items are in [Open questions](#open-questions).
>
> **Precedence:** a measurement on our board (§14) wins. Next comes BOARD_SETUP.md, then
> Arduino's general docs. [§13](#13-contrast-with-docsboard_setupmd) lists where BOARD_SETUP.md
> and Arduino's docs differ.
>
> Related: [CHALLENGE_CONTEXT.md](CHALLENGE_CONTEXT.md) (strategy and open questions).

---

## 1. Identity

| Item | Value | Source |
|---|---|---|
| Product | Arduino® UNO™ Q **4 GB** ("Dual-Brain SBC for AI & IoT") | store |
| SKU | **ABX00173** (the 2 GB / 16 GB variant is ABX00162) | store, datasheet |
| Price | €82.90 incl. VAT | store |
| Weight | 0.048 kg | store |
| Barcode / TARIC (EU customs tariff code) | 7630049205727 / 8742900 | store |
| Manufacturer | Arduino S.r.l., Via Andrea Appiani 25, 20900 Monza, Italy | datasheet |
| Linux device-tree id | `arduino,imola` (`cat /sys/firmware/devicetree/base/compatible`) | llama.cpp guide |
| Intended use | Development and prototyping. Security is the builder's responsibility | datasheet |

The two variants share one datasheet. Only RAM and eMMC differ:

| Variant | RAM | Storage |
|---|---|---|
| ABX00162 | 2 GB | 16 GB |
| **ABX00173 (ours)** | **4 GB** | **32 GB** |

---

## 2. Architecture in one picture

The UNO Q has two processors, joined by an RPC layer called **Bridge**. The **MPU**
(microprocessor unit) runs Linux. The **MCU** (microcontroller unit) runs real-time code.

```text
 ┌──────────────── MPU: Qualcomm Dragonwing QRB2210 ───────────────┐      ┌──── MCU: STM32U585 ────┐
 │ 4× Cortex-A53 @ 2.0 GHz · Adreno 702 GPU · Debian Linux          │      │ Cortex-M33 @ 160 MHz   │
 │ 1.8 V I/O · LLMs, Python, Docker, camera, display, Wi-Fi, BT     │◄────►│ Zephyr + Arduino core  │
 │ 4 GB LPDDR4X · 32 GB eMMC                                        │Bridge│ 3.3 V I/O · ADC, PWM,  │
 └──────────────────────────────────────────────────────────────────┘ RPC  │ CAN, LED matrix, Qwiic │
                                                                          └────────────────────────┘
```

- The **MPU** runs everything heavy: Linux, Python, llama.cpp, embeddings, App Lab apps (§7.2).
- The **MCU** runs real-time work and the 3.3 V headers. It is irrelevant to language-model inference.
- **Bridge** (`arduino-router` daemon, MessagePack RPC over a Unix socket) lets sketches call Linux
  services and lets Linux call MCU functions. Details in §10.

---

## 3. Specifications

### 3.1 Application processor (MPU)

| Item | Value |
|---|---|
| SoC | Qualcomm Dragonwing **QRB2210** |
| CPU | 4× Arm **Cortex-A53** @ 2.0 GHz, 64-bit (ARMv8.0-A) |
| GPU | **Adreno 702** @ 845 MHz, unified memory shared with system RAM |
| ISP | Dual: 13 MP + 13 MP, or 25 MP, @ 30 fps |
| MPU I/O | USB 3.1 with role switching, SDIO 3.0, 4-lane MIPI-CSI-2, 4-lane MIPI-DSI |
| OS | Debian Linux ("upstream support") |
| NPU | **None published.** Datasheet lists no NPU or DSP compute figure |
| I/O voltage | 1.8 V. Absolute maximum 2.1 V |

### 3.2 Microcontroller (MCU)

| Item | Value |
|---|---|
| Chip | STMicroelectronics **STM32U585** |
| Core | Arm Cortex-M33 up to 160 MHz, with FPU |
| Memory | 2 MB flash, 786 kB SRAM |
| OS | Arduino Core on Zephyr OS |
| I/O voltage | 3.3 V |
| Peripherals used | ADC, DAC, PWM, CAN (FDCAN1), UART, SPI, I²C, OPAMP, LED matrix |

### 3.3 Memory and storage

| Item | Value |
|---|---|
| RAM | **4 GB LPDDR4X**, single rank, 32-bit |
| Usable by Linux | **3.6 GiB total**, about **2.9 GiB available** when idle (measured, §14.1). Arduino's llama.cpp guide says "about 3.6 GB free" |
| GPU memory | "Available video memory" 1740 MB, **shared** with RAM |
| Storage | **32 GB eMMC**, holds the OS and data |
| Root filesystem | Described as "small". On our board `/` is a separate 9.8 GB partition and **`/home/arduino` is 18 GB** (measured, §14.1) |

### 3.4 Wireless

| Item | Value |
|---|---|
| Module | WCBN3536A (Qualcomm WCN3980) |
| Wi-Fi | Wi-Fi 5, 802.11a/b/g/n/ac, dual band 2.4 / 5 GHz |
| Bluetooth | 5.1 (Classic and BLE) |
| Link to MPU | SDIO for Wi-Fi data, UART for Bluetooth control |
| Antenna | One shared on-board PCB antenna |
| Max transmit power (EIRP: effective isotropic radiated power) | BT Classic 15 dBm, BLE 9.5 dBm. Wi-Fi 2.4 GHz 19.59 dBm EIRP, Wi-Fi 5 GHz 17.64 dBm EIRP (13.95 dBm in the upper 5725–5875 MHz band) |
| Radio notes | 5.15–5.35 GHz is indoor-only. Keep 20 cm between the radiator and a person |

### 3.5 USB-C port (the only built-in port)

| Item | Value |
|---|---|
| Standard | USB 3.1 Gen 1 (5 Gb/s), with host/device **role switching** |
| Power in | USB-PD sink, requests **5 V / 3 A (15 W) only**. No higher-voltage profile |
| Video out | DisplayPort Alt-Mode through the ANX7625 bridge. Up to 1920×1080, best at **1280×720** |
| Display sharing | USB-C DisplayPort and the JMEDIA DSI header are **multiplexed**: only one is active |
| Alt-Mode cost | When DisplayPort is active, USB data speed drops |
| Needs a dongle for | HDMI, Ethernet, microSD, USB drive, keyboard, mouse, USB camera, USB or 3.5 mm audio |
| Apple USB-C dongle | Tested and **incompatible** (SBC guide) |

### 3.6 On-board UI

| Item | Detail |
|---|---|
| LED matrix | 8 × 13 monochrome blue (104 pixels), driven by the MCU. Shows the boot logo for about 20–30 s during Linux startup |
| RGB LED 1 (Linux) | `red:user` GPIO_41, `green:user` GPIO_42, `blue:user` GPIO_60. Via `/sys/class/leds/` |
| RGB LED 2 (Linux) | `red:panic` GPIO_39, `green:wlan` GPIO_40, `blue:bt` GPIO_47. Shows system status by default |
| RGB LEDs 3 and 4 (MCU) | LED3: PH10/PH11/PH12. LED4: PH13/PH14/PH15 (R/G/B) |
| Polarity | RGB LEDs are **active low** (logic 0 = on) |
| Power LED | Green, lit whenever the 3.3 V rail is up |
| Power button (JBTN1) | Hold **≥ 5 s** to reboot Linux. It does not cut power. The board boots by itself when powered |

### 3.7 Mechanical

| Item | Value |
|---|---|
| Size | 68.58 mm × 53.34 mm (datasheet). Store page says 68.85 mm, likely a typo: the datasheet matches the UNO outline (§13.3) |
| Form factor | Arduino UNO, compatible hole pattern |
| Bottom parts | Below 2 mm, so it stacks on carrier bases |
| Operating temperature | −10 °C to +60 °C (ambient near the board) |
| CAD | STEP files on docs.arduino.cc |

---

## 4. Power

### 4.1 Input options

| Source | Voltage | Current | Where |
|---|---|---|---|
| USB-C VBUS | 5 V (4.5–5.5 V) | up to 3 A | USB-C |
| VIN (DC in) | **7–24 V** | not specified | JMEDIA, JANALOG |
| 5V_SYS pin | 5 V | up to 3 A | JANALOG, JMISC, JSPI |

- USB-C VBUS and the 7–24 V buck output are **diode-OR'd** onto `5V_SYS`.
- **Use a 5 V / 3 A supply and cable.** Wireless bursts and display start-up cause short current peaks,
  and a weak supply gives undervoltage and resets.
- Store FAQ: a non-PD supply **will not boot** the board. It recommends at least 15 W.
- Reverse polarity was tested at −24 V on DC IN, but the official docs specify operation
  only with the correct polarity.
- Powering from the 5 V or VIN pins does not enable USB host mode. JCTL is 1.8 V. Never apply
  3.3 V or 5 V to it. To force host mode, follow Arduino's
  [Force USB host mode guide](https://github.com/arduino/docs-content/tree/main/content/hardware/uno/boards/uno-q/tutorials/guides/host-mode):

    1. Disconnect the power supply.
    2. Short GND (JCTL pin 1 or 7) to VOL_DOWN (JCTL pin 3).
    3. Connect the power supply again.

### 4.2 Rails

| Rail | Voltage | Source |
|---|---|---|
| `5V_SYS` | 5.0 V | Diode-OR of USB-C VBUS and the VIN buck |
| `PWR_3P8V` | 3.8 V | Buck from `5V_SYS`. Reserved for future use |
| `PWR_3P3V` | 3.3 V (3.1–3.5 V) | Buck from `PWR_3P8V`. Feeds the MCU, Wi-Fi 3.3 V, headers |
| `VREG_L15A_1P8V` | 1.8 V | Low-dropout regulator (LDO) in the PM4125 power-management IC (PMIC). Feeds SoC I/O, ANX7625, level shifters |
| `VBAT` | 3.8 V | Reserved for system use |
| `VCOIN` | n/a | Powers only the PMIC real-time clock |

### 4.3 Limits and tolerances

| Parameter | Value |
|---|---|
| Processor I/O (JMEDIA, JMISC, JCTL) | 1.8 V nominal, **2.1 V absolute max**. Never drive with 3.3 V |
| Maker I/O (JDIGITAL, JANALOG) | 3.3 V nominal, 3.6 V absolute max |
| ADC inputs (A0–A5) | 0 to VREF+ (about 3.3 V), **not 5 V tolerant**. Max VDD + 0.3 V |
| D3 (PB0) | 3.6 V tolerant only, **not 5 V tolerant in any mode** |
| Most other digital pins | 5 V tolerant as inputs, outputs drive 3.3 V |
| Per-pin current | Follow the STM32U585 limits. Store FAQ: about 20 mA typical, use a driver for loads |
| Header power | Shared with on-board loads. The official docs give no fixed current budget |

Schottky diode-OR drop (forward voltage): 0.35 V at 1.0 A, 0.37 V at 1.5 A, 0.39 V at 2.0 A.

**Power consumption:** the official docs give **no idle or load wattage** for the UNO Q.
See [Open questions](#open-questions).

---

## 5. Connectors and pinout

The UNO Q has eight headers. The 3.3 V ones follow the UNO layout. Full pin tables are in the
datasheet. See also the
[full pinout PDF](https://docs.arduino.cc/resources/pinouts/ABX00162-full-pinout.pdf).

| Header | Pins | Voltage | Purpose |
|---|---|---|---|
| **JDIGITAL** (A2) | 18 | 3.3 V | D0–D13, D20, D21, AREF, GND. UART, SPI, I²C, PWM, CAN |
| **JANALOG** (A3) | 14 | 3.3 V | A0–A5 (ADC, DAC, I²C3), IOREF, RESET, BOOT, 3V3, 5V, VIN, GND |
| **JSPI** (A5) | 6 | 3.3 V | MISO, SCK, MOSI, MCU reset, 5V_SYS, GND |
| **Qwiic** (A4) | 4 | 3.3 V | I²C (SDA = PD13, SCL = PD12). Plug-in for Modulino nodes |
| **JMEDIA** (B2) | 60 | 1.8 V | MIPI DSI (4 lanes), MIPI CSI0 and CSI1 (4 lanes each), camera I²C and clocks, 3V3 out, VIN in |
| **JMISC** (B1) | 60 | mixed | MCU PSSI, SDMMC1, TRACE, I²C4, OPAMP1. Audio (mic, headphone, line out, earpiece). MPU GPIO at 1.8 V. Power rails |
| **JCTL** (A1) | 10 | 1.8 V | Debug UART console (SE4), USB boot, PMIC reset, VBUS disable, volume buttons |
| **USB-C** | 1 | — | See §3.5 |

### 5.1 JDIGITAL (UNO digital header)

| Pin | Name | MCU pin | Functions |
|---|---|---|---|
| 1 | D0 | PB7 | USART1_RX |
| 2 | D1 | PB6 | USART1_TX |
| 3 | D2 | PB3 | TIM2_CH2 |
| 4 | ~D3 | PB0 | PWM (TIM3_CH3), OPAMP2 out. Not 5 V tolerant |
| 5 | D4 | PA12 | FDCAN1_TX |
| 6 | ~D5 | PA11 | PWM, FDCAN1_RX |
| 7 | ~D6 | PB1 | PWM |
| 8 | D7 | PB2 | TIM8_CH4N |
| 9 | D8 | PB4 | TIM3_CH1 |
| 10 | ~D9 | PB8 | PWM |
| 11 | ~D10 | PB9 | PWM, SPI2_SS |
| 12 | ~D11 | PB15 | PWM, SPI2_MOSI |
| 13 | D12 | PB14 | SPI2_MISO |
| 14 | D13 | PB13 | SPI2_SCK |
| 15 | GND | — | Ground |
| 16 | AREF | — | Analog reference (not a GPIO) |
| 17 | D20 | PB11 | I2C2_SDA |
| 18 | D21 | PB10 | I2C2_SCL |

### 5.2 JANALOG (UNO analog and power header)

| Pin | Name | Net / MCU pin | Notes |
|---|---|---|---|
| 1 | BOOT | MCU_BOOT0 | Boot strap |
| 2 | IOREF | PWR_3P3V | Output only, do not back-feed |
| 3 | RESET | MCU_NRST | MCU reset |
| 4 | +3V3 | PWR_3P3V | 3.3 V out |
| 5 | +5V | 5V_SYS | Power in or out |
| 6, 7 | GND | — | Ground |
| 8 | VIN | DC_IN | 7–24 V in, power only |
| 9 | A0 / D14 | PA4 | ADC, DAC0. Not 5 V tolerant |
| 10 | A1 / D15 | PA5 | ADC, DAC1. Not 5 V tolerant |
| 11 | A2 / D16 | PA6 | ADC, OPAMP2 in+ |
| 12 | A3 / D17 | PA7 | ADC, OPAMP2 in− |
| 13 | A4 / D18 | PC1 | ADC, I2C3_SDA. Pull-ups to 3.3 V only |
| 14 | A5 / D19 | PC0 | ADC, I2C3_SCL. Pull-ups to 3.3 V only |

### 5.3 Smaller headers

**Qwiic**

| Pin | Name |
|---|---|
| 1 | GND |
| 2 | +3V3 |
| 3 | SDA (PD13) |
| 4 | SCL (PD12) |

**JSPI** (chip select comes from a GPIO)

| Pin | Name |
|---|---|
| 1 | MISO (PC2) |
| 2 | +5V |
| 3 | SCK (PD1) |
| 4 | MOSI (PC3) |
| 5 | RESET |
| 6 | GND |

**JCTL** (1.8 V)

| Pin | Name |
|---|---|
| 1 | GND |
| 2 | USB_BOOT |
| 3 | VOL_DOWN (GPIO_36) |
| 4 | SE4 TX (console) |
| 5 | VOL_UP (GPIO_96) |
| 6 | SE4 RX (console) |
| 7 | GND |
| 8 | PMIC_RESET |
| 9 | +1V8 out |
| 10 | VBUS_DISABLE |

### 5.4 JMISC and JMEDIA (60 pins each)

Read the datasheet for the full tables. Key facts:

- **JMISC** pins 1–25 are 3.3 V MCU signals (PSSI D0–D7 parallel camera bus, SDMMC1, TRACE, I²C4,
  MCO, CRS_SYNC, OPAMP1). The datasheet interleaves the next pins:

    - Analog audio (mic 2 in+/in−/bias, headphone L/R/REF, line out P/M, earpiece, headset
      detect): pins 28–34, 36, 38, 40 and 42.
    - **1.8 V** MPU GPIO: pins 37, 39, 41, 43 and 45–52.
    - GND: pins 26, 27, 35 and 44.
    - Pins 53–60 carry 3V3, 5V_SYS, 1V8, VCOIN and VBAT.

- **JMEDIA** pins 3–18 carry the DSI lanes, pins 21–48 and 52–54 carry the CSI0 and CSI1 lanes.
  Camera control I²C (CCI, GPIO_22/23/29/30) and camera master clocks (GPIO_20/21) are 1.8 V.
  Pins 57–60 are VIN and 3V3.
- SoC GPIO on JMISC is interface-dedicated, not general maker GPIO. MIPI lanes are D-PHY pairs.
  Do not add pull-ups to them. Do not reuse the I²C, CCI or MI2S0 lines as plain GPIO.
- **Debug console:** the JCTL UART (SE4) is the Linux serial console, **1.8 V**, 115200 baud.
  It shows boot and U-Boot logs before SSH or adb exist. Use a 1.8 V USB-to-TTL adapter.

---

## 6. Graphics, video and compute acceleration

### 6.1 GPU APIs (Mesa open-source drivers)

| API | Driver | Version exposed |
|---|---|---|
| OpenGL | freedreno | 3.1 (device name FD702) |
| OpenGL ES | freedreno | 3.1 |
| Vulkan | turnip | Hardware supports 1.1. Driver exposes **1.0.318** |
| **OpenCL** | Mesa | **2.0** |

- GPU limits: 2D texture 16384², 3D texture 2048³, GLSL 1.40, GLSL ES 3.10.
- Standard Mesa tools (`mesa-utils`, `vulkan-tools`) work. Arduino ships no UNO Q-specific GPU examples.

### 6.2 Hardware video codecs (V4L2, `/dev/video0` and `/dev/video1`)

| Codec | Encode | Decode | GStreamer element |
|---|---|---|---|
| H.264 | Yes | Yes | `v4l2h264enc` / `v4l2h264dec` |
| H.265 | Yes | Yes | `v4l2h265enc` / `v4l2h265dec` |
| VP9 | No | Yes | `v4l2vp9dec` |

Up to 1920×1080. Not relevant to a text copilot, but useful for a camera demo.

### 6.3 What this means for the language model (our project)

- The official docs mention **OpenCL 2.0 via Mesa**, but they do **not** say llama.cpp's OpenCL backend
  works on it. llama.cpp's Adreno OpenCL backend targets the Qualcomm proprietary driver on high-end
  parts. Arduino's own guide runs **CPU-only**, and so does the pinned build in BOARD_SETUP.md, so
  **the CPU path is the contest path**. A GPU test is an optional side experiment (see [Open questions](#open-questions)).
- The GPU shares the 4 GB of system RAM. Offloading layers does not add memory.
- The official docs list **no NPU** and no DSP path. Plan for CPU inference.
- Cortex-A53 has no SDOT or I8MM instructions. ✅ **Confirmed on our board** (§14.2): the CPU flags list `asimd` but no `asimddp` and no `i8mm`.

---

## 7. Software environment

### 7.1 Linux (Debian)

- Full Debian on the MPU. The OS supports Docker and Docker Compose. Python 3 is present.
- No compiler toolchain and no passwordless `sudo` out of the box (llama.cpp guide). **Our setup
  installs the toolchain with `sudo apt-get` and builds llama.cpp on the board** (BOARD_SETUP steps 2–3).
- User: `arduino`. **Project password: `opensource`**, set in App Lab first setup (BOARD_SETUP 0.1).
  It is also the `sudo` password. Arduino's ADB guide mentions `arduino` as a pre-setup fallback.
  The datasheet says there is no documented default. Do not rely on either.
- Wi-Fi from the shell: `sudo nmcli d wifi connect <SSID> password <PASSWORD>`, or `nmtui`.
- Safe shutdown: run `sudo poweroff`. Then wait. Do not pull power during writes.
- First boot takes 20–30 s. Wait for the LED-matrix animation to finish.

### 7.2 Arduino App Lab

| Item | Detail |
|---|---|
| What it is | Editor that builds, deploys and runs an **App** on both processors |
| An App contains | A Python program (Linux), an optional Arduino sketch (MCU), optional **Bricks** |
| Bricks | Prepackaged services (AI models, web UI, REST, data sources) deployed with the App |
| LLM Brick | `arduino:llm` wraps local llama.cpp inference. Our project does not use it, and we have not measured it |
| Modes | **PC-hosted** (USB data cable for first setup, then network) and **SBC** (runs on the board) |
| Host OS | Windows 10+ (64-bit), macOS 11+ (64-bit), Ubuntu 22.04+ or Debian Trixie (64-bit) |
| First setup | Names the board, sets the Linux password, joins Wi-Fi, enables SSH, updates the board |
| Run time | Compiling the sketch and starting Python can take up to a minute per run |
| Logs | Console tabs: Start-up, Main (Python), Sketch (serial) |
| CLI | `arduino-app-cli` starts and stops Apps from the shell. Apps live in `~/ArduinoApps/` |
| Caveat | While an App runs, USB interfaces may be occupied. Stop the App to use CLI tools over USB |

Other ways to program the MCU: Arduino IDE 2.0+ (MCU only), Arduino CLI with VS Code.

### 7.3 Flashing and recovery

- **App Lab → Settings**: reset or switch the Linux image, optionally keeping user data.
- **Arduino Flasher CLI**: reinstall the OS when the board is unresponsive or not on the network.
- A forced USB boot input exists on JCTL (`USB_BOOT`). Details: Arduino's "Flash a Linux Image" tutorial (not read, see [Sources](#sources)).

---

## 8. Accessing the board

| Method | Command | Notes |
|---|---|---|
| **SSH (Wi-Fi)** | `ssh arduino@<boardname>.local` or `ssh arduino@<ip>` | App Lab first setup enables SSH |
| **ADB (USB)** | `adb devices`, then `adb shell` | Can take up to a minute to appear. Needs `android-sdk-platform-tools` |
| **SBC mode** | Keyboard, mouse and HDMI through a USB-C dongle | Desktop login as `arduino` |
| **Debug UART** | JCTL header, 1.8 V, 115200 baud | Works before the network is up |
| **Remote desktop** | Xrdp, RustDesk or Tailscale + SSH | See the [Remote Access guide](https://docs.arduino.cc/tutorials/uno-q/remote-access/) |

- **mDNS blocked?** Use the IP address. Find it with `hostname -I` on the board. Some networks
  (university Wi-Fi) block `.local` names.
- **Copy files:** `scp file arduino@<boardname>.local:/home/arduino/` (use `-rp` for folders).
  Over USB: `adb push` and `adb pull`.
- **Several boards on USB:** `export ANDROID_SERIAL=<serial>`.

---

## 9. Running a language model on the board (official guide)

> **Not our procedure.** This is Arduino's generic tutorial (prebuilt binary, `Q4_K_M`, port 8080).
> Our project builds llama.cpp at a pinned commit and serves Q8_0 models on ports 8081 and 8082.
> Follow [BOARD_SETUP.md](BOARD_SETUP.md). See §13.

GGUF is llama.cpp's model file format. `Q4_K_M` (4-bit) and `Q8_0` (8-bit) are two of its
quantization types. Speeds are in tokens per second (tok/s). See
[Token](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md) in the glossary.

Arduino's own tutorial is "Running Llama.cpp with Qwen3.5-0.8B on the Arduino UNO Q". It downloads
a prebuilt llama.cpp release and a `Q4_K_M` model. Then it runs `llama-cli` and `llama-server` on
port 8080. Its commands are in Arduino's
[llama.cpp guide](https://github.com/arduino/docs-content/tree/main/content/hardware/uno/boards/uno-q/tutorials/guides/llama-cpp).

| Fact | Value |
|---|---|
| Model | Qwen3.5-0.8B `Q4_K_M`, about 500 MB (unsloth GGUF) |
| Official speed | About **8.4 tok/s prompt, 3.6 tok/s generation**, CPU only |
| The organizers' measurement ([BOARD_SETUP.md](BOARD_SETUP.md)) | About 11 tok/s prompt and about 6 tok/s generation with Qwen3.5 0.8B Q8_0 |
| Our measurement (§14.3) | **10.1 tok/s prompt and 4.8 tok/s generation** with Qwen3.5 0.8B Q8_0 |
| Free RAM | The guide says about 3.6 GB free. We measured 3.6 GiB total and about 2.9 GiB available (§14.1). Enough for a small 4-bit model, not for large F16 models |
| Disk | Keep about 1 GB free. The guide discourages a build from source (no toolchain, little disk) |

Earlier third-party measurements are in [CHALLENGE_CONTEXT.md](CHALLENGE_CONTEXT.md) §2.

---

## 10. Bridge / RPC (MCU ↔ Linux)

- **Router:** the `arduino-router` systemd service is a hub (star topology). Many Linux processes
  can talk to the MCU at once. It also routes Linux-to-Linux calls and keeps a directory of services.
- **Protocol:** MessagePack-RPC over a Unix socket. Message types: request, response, notification.
- **App Lab API:** Python `Bridge` on Linux, `Bridge` library in sketches (call or notify).
- **Custom clients:** C++ or plain Python over the socket (see the [RouterBridge multilanguage guide](https://docs.arduino.cc/tutorials/uno-q/routerbridge-multilanguage/)).
- Troubleshooting areas in that guide: connection failed, timeout waiting for a response.
- **Not needed for the language model.** Use it only if the copilot should drive the LED matrix, buttons or sensors.

---

## 11. Security notes (from Arduino's hardening guide)

Topics covered:

- password and access control
- login auditing
- OS updates
- physical access (debug UART, USB boot)
- network exposure (firewall, services bound to localhost)
- TLS for web services (mkcert)
- data protection
- log forwarding and monitoring

For the datathon, the useful rules are:

- keep the model services on `127.0.0.1`
- change default credentials
- do not expose ports to the school network

---

## 12. Certifications

CE (RED 2014/53/EU), UKCA, FCC (Class B, Part 15), ISED (RSS-247), MIC, KC, SRRC (ABX00162 CMIIT ID
26J996Q0A162, ABX00173 CMIIT ID 26J996Q0A173), WPC, Anatel, ICASA, IMDA, NCC, OFCA, RCM. Declarations
of conformity: <https://docs.arduino.cc/certifications/>. Radio equipment must stay 20 cm from the body.

---

## 13. Contrast with `docs/BOARD_SETUP.md`

[BOARD_SETUP.md](BOARD_SETUP.md) is the organizers' guide, pinned at commit `d6e3f1b`. Each row
below is a conflict or a gap in Arduino's documentation. The last column shows how BOARD_SETUP.md
settles it. Where §14 measured the same thing, the measurement wins (see the precedence rule at the top).

### 13.1 Resolved by BOARD_SETUP.md

| Topic | Arduino docs said | BOARD_SETUP.md says |
|---|---|---|
| Linux password | Unclear: `arduino` in the ADB guide, none in the datasheet | Set it in App Lab as **`opensource`** (step 0.1). Same password for SSH and `sudo` |
| Toolchain | No compiler, no passwordless `sudo`. Use a prebuilt binary | `sudo apt-get install build-essential cmake git pkg-config libssl-dev curl wget ca-certificates python3 sqlite3 jq` (step 2) |
| llama.cpp source | Newest prebuilt `ubuntu-arm64` release (`b10644`) | **Build from source** at pinned commit `2cbe0ec` with `-DGGML_NATIVE=ON -DCMAKE_BUILD_TYPE=Release`, about 30 min (step 3). Pinned so every team's results compare |
| Language model | Qwen3.5-0.8B **Q4_K_M**, about 500 MB | Qwen3.5 0.8B **Q8_0**, 835 MB, SHA256-checked (step 4) |
| Embedding model | Not covered | bge-small-en-v1.5 Q8_0, 37 MB, 384 dimensions |
| Server ports | `llama-server` on 8080 (guide). 9999 for the App Lab LLM Brick (third-party report) | **8081** language model, **8082** embeddings, **8083** optional vision. All bound to `127.0.0.1` |
| Server flags | Defaults | `--threads 4 --ctx-size 4096 --parallel 1 --cache-ram 0 --ctx-checkpoints 2 --jinja --reasoning off --reasoning-budget 0 --alias qwen3.5-0.8b` (language model, [`math-llm.service`](https://github.com/Sigkaio636/Santolina_tutor/blob/main/board/systemd/math-llm.service)). With default flags, the kernel's out-of-memory killer stopped the server |
| Custom model path | App Lab's LLM Brick, or our own server? | Own `llama-server` run as **systemd services** `math-llm` and `math-embed`, started at boot (step 7). App Lab runs next to them |
| Free RAM and swap | "About 3.6 GB free" | The organizers: `free -h` shows **3.6 GiB total, about 3.1 GiB available, 1.8 GiB swap** on a fresh board. Both model services use about **1.1 GB**, leaving about **2.5 GB**. We measured about **920 MiB** used and about **2.7 GiB** available (§14.4) |
| Disk | "Small root filesystem", keep 1 GB free | Need **≥ 2 GB free** (`df -h ~`). Build about 350 MB, models 870 MB, packages a few hundred MB |
| Speed | Official: 8.4 tok/s prompt, 3.6 tok/s generation (Q4_K_M) | The organizers: about **11 tok/s read, about 6 tok/s write**. We measured 10.1 and 4.8 tok/s (§14.3). One-letter answer about 9 s, so the 60 s per-problem limit is the budget |
| Network access | `.local` mDNS name | Use the **IP address** (`hostname -I`). SSH `arduino@<ip>`. `adb shell` as fallback, and for demos with Wi-Fi off (steps 0.2–0.4) |
| Internet | Needed for the Arduino guide | Needed for steps 2–4, and for step 8.1, which clones the repository on the board. Copy it with `scp -r` or `adb push` to avoid that. Afterwards everything runs **offline** (a contest rule) |
| GPU / OpenCL | Mesa OpenCL 2.0 exists, llama.cpp gain unconfirmed | The pinned build is **CPU-only** (`GGML_NATIVE`, NEON). No OpenCL or Vulkan flags. The CPU path is the contest path. GPU stays an optional experiment |
| Power | 15 W recommended (store) vs 5 V / 3 A (datasheet) | Both agree: **5 V, 3 A USB-C supply** (BOARD_SETUP "What you need") |
| Shutdown | `sudo poweroff` | Same (step 0.5). Never pull power while it writes |
| Ethernet and dongles | Store FAQ mentions Ethernet, no port on the board | Not used. The board and the laptop share **one Wi-Fi network** |
| Debian toolchain versions | Not stated | The expected outputs show gcc 14.2, cmake 3.31, Python 3.13.5 (Debian 13 "trixie", measured in §14.1) |

### 13.2 Not covered by BOARD_SETUP.md

BOARD_SETUP.md does not cover power draw, temperature and throttling, the GPU, or the speed gap with
Arduino's figures. These items are in [Open questions](#open-questions).

### 13.3 Cosmetic discrepancies inside the Arduino docs (no action)

| Topic | Detail |
|---|---|
| Board size | Store 68.85 mm, datasheet 68.58 mm. Trust the datasheet |
| File names | Datasheet and schematics URLs say ABX00162, the product is ABX00173. One document covers both |
| Page coverage | The live user manual and App Lab pages were not fetchable. The content here comes from Arduino's `docs-content` GitHub repo. `support.arduino.cc` returned HTTP 403, so the "code repositories for App Lab components" article was **not read** |

---

## 14. Measured on our board (2026-11-14)

We measured everything below on our 4 GB UNO Q while we followed `docs/BOARD_SETUP.md` steps 0 to 8.
These are measurements, not Arduino's published figures.

### 14.1 System

| Item | Measured |
|---|---|
| Model string | `Arduino SA,Imola`, device tree `arduino,imola` / `qcom,qrb2210` |
| OS | Debian GNU/Linux 13 (trixie), aarch64, kernel 6.16.7 |
| CPU | 4 cores |
| RAM | 3.6 GiB total, about 2.9 GiB available when idle, 1.8 GiB swap |
| Root `/` | 9.8 GB partition (`mmcblk0p68`), 4.9 GB free after the App Lab update |
| Home `/home/arduino` | **18 GB partition** (`mmcblk0p69`), about 15 GB free after llama.cpp and both models |
| Clock | Synchronized once Wi-Fi is up. Not synchronized before the App Lab first setup |
| Network | The Linux side reports two addresses: Docker's `172.17.0.1` and the Wi-Fi address. Use the Wi-Fi one |
| Tools present | `adb shell` logs in as `arduino` with no password. `sudo` needs the project password |

### 14.2 CPU flags (answers an open question)

```text
Features : fp asimd evtstrm aes pmull sha1 sha2 crc32 cpuid
```

No `asimddp` (dot product) and no `i8mm`. int8 and int4 matrix multiplication gets no hardware
speedup on this CPU. Whether memory bandwidth limits decoding is in
[Open questions](#open-questions).

### 14.3 Speed

| Measurement | Value |
|---|---|
| Prompt reading (Qwen3.5 0.8B Q8_0, 27 tokens) | **10.1 tok/s** |
| Writing (10 tokens) | **4.8 tok/s** |
| "7 times 8" question, end to end | 4.6 s |
| One letter A–E, grammar-constrained (the server can output only A–E), 62-token prompt | a few seconds |
| Smoke test, 5 sample problems | **5.6–7.0 s each**, limit 60 s |
| Embedding (bge-small, 3 sentences) | 384 dimensions in 0.18 s |
| Embedding quality check | similar pair 0.86, unrelated pair 0.52 |

The organizers quote about 11 tok/s reading and about 6 tok/s writing. Our numbers are close, and lower on writing.

### 14.4 Build and services

| Item | Result |
|---|---|
| llama.cpp | Built from source at pinned commit `2cbe0ec`, `-DGGML_NATIVE=ON`, Release, `-j4`, **about 25 minutes**. `llama-server --version` reports `0.9.0-dev (build 1, commit 2cbe0ec)` with GNU 14.2.0 |
| Models | `Qwen_Qwen3.5-0.8B-Q8_0.gguf` (835 MB) and `bge-small-en-v1.5-q8_0.gguf` (37 MB), both SHA256-checked |
| Services | `math-llm` (8081) and `math-embed` (8082), both **active and enabled at boot**, listening only on `127.0.0.1` |
| Memory with both services up | about 920 MiB used, about 2.7 GiB available |
| Health script | `board/00_check_board.sh` reports "The board looks healthy" |
| Smoke test | `board/05_smoke_test.sh` passes: servers answer, embeddings look right, 5 valid letters, worst latency 7.0 s |
| Baseline accuracy | 0/5 on the sample problems, every answer `A` (the baseline's letter bias). This checks the pipeline, not quality |

### 14.5 History of the first setup (2026-11-14)

- `apt` showed a "Daemons using outdated libraries" dialog (`needrestart`) after the package
  install. We chose `<Cancel>`. Nothing needed a restart for the build. Restarting
  `arduino-router`, `arduino-app-cli`, `containerd` or `avahi` can drop your `adb` or SSH session.
- We ran the build and the downloads with `nohup` over `adb shell`, so a dropped SSH session could
  not stop them. See [What to try](#what-to-try).
- During the first setup, the board used the organizers' clone
  `~/datathon-UPC-maths-qualcomm-arduino-unoq` (commit `d6e3f1b`). The board now runs our repository,
  `~/Santolina_tutor` (see [Deploy the copilot on the board](how-to/deploy-copilot-on-board.md)).
  [BOARD_SETUP.md](BOARD_SETUP.md) lists, in its source note, our local edits to the files copied
  from that commit. After that, we added more files to our repository.

## 15. Measured on the laptop (Fedora 44)

- Arduino App Lab **0.12.0** runs on Fedora, although the store page lists only Ubuntu 22.04+ and
  Debian Trixie. All shared libraries resolved. The install steps are in [What to try](#what-to-try).
- The M3Kang preparation (BOARD_SETUP step 9) runs at about **0.8 rows/s** with RapidOCR on our
  laptop. That is about 70 minutes for English plus Catalan (about 3,500 rows). The organizers
  quote about 15 minutes per language.

## What to try

**Run a long job on the board so that a dropped session cannot stop it.** For example, the
llama.cpp build:

```bash
cd ~/Santolina_tutor
nohup ./board/02_build_llama_cpp.sh > ~/llama-build.log 2>&1 &
tail -f ~/llama-build.log
```

The build worked when the log ends with `Next: ./board/03_download_models.sh`. If llama-server
already exists at the pinned commit, the script stops at once with `Nothing to do.`

**Install App Lab on Fedora.**

1. Download the Linux x86-64 `.tar.gz` from the [Arduino software page](https://www.arduino.cc/en/software).
2. Unpack it: `mkdir -p ~/Applications && tar -xf <downloaded-file>.tar.gz -C ~/Applications`.
3. Install `webkit2gtk4.1` and `android-tools` (for `adb`) with `dnf`.
4. Add a udev rule for USB vendor IDs `2341` and `05c6`, with group `dialout` and mode `0666`.
   `adb` works with this rule alone, because mode `0666` opens the device to everyone.
5. Add yourself to the `dialout` group: `sudo usermod -a -G dialout $USER`. Then start a new login session.

## Open questions

- **Power draw.** No official idle or load figure, and none in BOARD_SETUP.md. Measure it with a USB
  power meter during inference. It matters for a battery or demo setup.
- **Temperature and throttling.** The operating range is −10 to +60 °C. Throttling under sustained
  load is not documented. Watch `/sys/class/thermal/*/temp` during a long `eval.py` experiment.
- **Decode speed limit.** We assume memory bandwidth limits decoding, so fewer bytes per
  weight would mean more tokens per second. This is not measured on our board.
- **GPU benefit.** Untested. Mesa OpenCL 2.0 exists, but no source confirms a llama.cpp gain. Optional test:
  build llama.cpp with OpenCL or Vulkan. Compare its speed with the CPU build. Read the speed from
  `llama-cli`'s timing output, or from the `timings` field of the server's answer (`prompt_per_second`,
  `predicted_per_second`). Our build has no `llama-bench`. Do not change the pinned build for the contest.
- **Speed gap with Arduino's figures.** Arduino's guide gets 3.6 tok/s writing (`Q4_K_M`). We measured
  4.8 tok/s (`Q8_0`, §14.3). The quantization and the llama.cpp build differ. For a cleaner comparison,
  run both models on the same build. Then compare the server's `timings`.

## Sources

Official pages (we read the docs.arduino.cc content from the source repository
[arduino/docs-content](https://github.com/arduino/docs-content), path `content/hardware/uno/boards/uno-q/`):

- Store page: <https://store.arduino.cc/products/uno-q-4gb>
- Product page: <https://docs.arduino.cc/hardware/uno-q/>
- Datasheet (rev. 16, 2026-10-30): [`datasheet/en-datasheet.md`](https://github.com/arduino/docs-content/blob/main/content/hardware/uno/boards/uno-q/datasheet/en-datasheet.md), PDF <https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf>
- Full pinout: <https://docs.arduino.cc/resources/pinouts/ABX00162-full-pinout.pdf>
- Schematics: <https://docs.arduino.cc/resources/schematics/ABX00162-schematics.pdf>
- User manual: <https://docs.arduino.cc/tutorials/uno-q/user-manual/>
- Power specification: <https://docs.arduino.cc/tutorials/uno-q/power-specification/>
- Single-board computer: <https://docs.arduino.cc/tutorials/uno-q/single-board-computer/>
- ADB: <https://docs.arduino.cc/tutorials/uno-q/adb/>
- SSH: <https://docs.arduino.cc/tutorials/uno-q/ssh/>
- Remote access: <https://docs.arduino.cc/tutorials/uno-q/remote-access/>
- Debian guide: <https://docs.arduino.cc/tutorials/uno-q/debian-guide/>
- Router / Bridge RPC: <https://docs.arduino.cc/tutorials/uno-q/routerbridge-multilanguage/>
- Security hardening: <https://docs.arduino.cc/tutorials/uno-q/security-hardening-guide/>
- Force USB host mode: [`tutorials/guides/host-mode/`](https://github.com/arduino/docs-content/tree/main/content/hardware/uno/boards/uno-q/tutorials/guides/host-mode)
- llama.cpp with Qwen3.5-0.8B: [`tutorials/guides/llama-cpp/`](https://github.com/arduino/docs-content/tree/main/content/hardware/uno/boards/uno-q/tutorials/guides/llama-cpp)
- Certifications: <https://docs.arduino.cc/certifications/>
- App Lab: <https://www.arduino.cc/en/software>
- Forum: <https://forum.arduino.cc/c/hardware/uno-familyd/uno-q/222>
- STM32U585 datasheet: <https://www.st.com/resource/en/datasheet/stm32u585ai.pdf>
- Qualcomm QRB2210: <https://www.qualcomm.com/products/internet-of-things/robotics-processors/qrb2210>

We did not read these pages (blocked or not fetched):

- the user manual and App Lab quickstart through the live site
- `support.arduino.cc` articles
- the App Lab Bricks reference
- the Flash a Linux Image tutorial

We read the user manual and the Debian, remote-access and hardening guides only for their structure
and the sections quoted above.
