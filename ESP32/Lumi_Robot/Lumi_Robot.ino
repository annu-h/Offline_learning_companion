// ================================================================
// Lumi Robot - ESP32 Firmware
// Offline Learning Companion
// ================================================================
// Target Board: ESP32 Dev Module
// Description: Controls microphone input, speaker output, RTC,
//              SD card, and push button with serial command interface.
// ================================================================

// ================================
// PIN CONFIGURATION
// ================================
// All GPIO assignments defined at the top for clarity and conflict checking.
// No pins are shared between peripherals.
//
// INMP441 I2S Microphone (I2S0 - Input)
//   - GPIO 14: BCK (Serial Clock)
//   - GPIO 15: WS  (Word Select / LRCK)
//   - GPIO 32: SD  (Serial Data) - INPUT_ONLY capable pin
//
// MAX98357A I2S Amplifier (I2S1 - Output)
//   - GPIO 25: BCK (Serial Clock)
//   - GPIO 26: WS  (Word Select / LRCK)
//   - GPIO 27: SD  (Serial Data / DIN)
//
// DS3231 RTC (I2C)
//   - GPIO 21: SDA (Data)
//   - GPIO 22: SCL (Clock)
//
// MicroSD Card Module (SPI - VSPI)
//   - GPIO  5: CS   (Chip Select)
//   - GPIO 19: MISO (Master In Slave Out)
//   - GPIO 23: MOSI (Master Out Slave In)
//   - GPIO 18: SCK  (Clock)
//
// Push Button
//   - GPIO 33: Button input with internal pull-up
//   (GPIO 33 is not a strapping pin, safe for general use)
//
// Pin Conflict Check:
//   I2S0 pins {14, 15, 32} -- no overlap with other peripherals
//   I2S1 pins {25, 26, 27} -- no overlap with other peripherals
//   I2C pins  {21, 22}      -- no overlap with other peripherals
//   SPI pins  {5, 18, 19, 23} -- no overlap with other peripherals
//   Button pin {33}         -- no overlap with other peripherals
//
// ================================================================

// -------------------- INMP441 I2S Microphone --------------------
#define MIC_BCK_PIN     26    // I2S0 Serial Clock
#define MIC_WS_PIN      25    // I2S0 Word Select (LRCK)
#define MIC_DATA_PIN    33    // I2S0 Serial Data Input

// -------------------- MAX98357A I2S Amplifier -------------------
#define SPEAKER_BCK_PIN 27    // I2S1 Serial Clock
#define SPEAKER_WS_PIN  14    // I2S1 Word Select (LRCK)
#define SPEAKER_DATA_PIN 13   // I2S1 Serial Data Output (DIN)

// -------------------- DS3231 RTC (I2C) --------------------------
#define RTC_SDA_PIN     21    // I2C Data
#define RTC_SCL_PIN     22    // I2C Clock

// -------------------- MicroSD Card (SPI) ------------------------
#define SD_CS_PIN        5    // Chip Select
#define SD_MISO_PIN     19    // Master In Slave Out
#define SD_MOSI_PIN     23    // Master Out Slave In
#define SD_SCK_PIN      18    // Clock

// -------------------- Push Button -------------------------------
#define BUTTON_PIN      4    // Push button (active LOW with pull-up)

// -------------------- Audio Configuration -----------------------
#define SAMPLE_RATE     32000  // INMP441 operates at 32kHz
#define BITS_PER_SAMPLE 32    // INMP441 outputs 32-bit I2S samples
#define CHANNEL_COUNT    1    // Mono audio
#define BUFFER_SIZE     512   // I2S read/write buffer size
#define AUDIO_BLOCK_SIZE 1024 // Larger block for playback buffers

// -------------------- Button Debounce ---------------------------
#define BUTTON_DEBOUNCE_MS 200  // Debounce time in milliseconds

// ================================
// LIBRARIES
// ================================
#include <driver/i2s.h>    // ESP32 I2S driver for microphone and speaker
#include <Wire.h>          // I2C for DS3231 RTC
#include <SD.h>            // SD card via SPI
#include <SPI.h>           // SPI bus for SD card
#include <RTClib.h>        // DS3231 RTC library
#include <math.h>            // sqrt() for microphone test

// ================================
// GLOBALS
// ================================

// I2S buffers
static uint8_t i2s_rx_buffer[BUFFER_SIZE * 4];  // Receive buffer for mic
static uint8_t i2s_tx_buffer[BUFFER_SIZE * 4];  // Transmit buffer for speaker

// Button state
volatile bool buttonPressed = false;
unsigned long lastButtonTime = 0;
bool buttonEnabled = true;

// System state
bool systemInitialized = false;
bool listeningMode = false;
bool thinkingMode = false;
bool speakingMode = false;

// SD card file handle
File audioFile;

// RTC object
RTC_DS3231 rtc;
bool rtcInitialized = false;

// ================================
// FORWARD DECLARATIONS
// ================================
void setupHardware(void);
void setupMicrophone(void);
void setupSpeaker(void);
void setupRTC(void);
void setupSDCard(void);
void setupButton(void);
bool isButtonPressed(void);
void handleSerialCommands(void);
void processCommand(String command);
void cmdPING(void);
void cmdHELP(void);
void cmdSTATUS(void);
void cmdGET_TIME(void);
void cmdSET_TIME(String command);
void cmdMIC_TEST(void);
void cmdSD_STATUS(void);
void cmdSD_LIST(void);
void cmdLISTENING(void);
void cmdTHINKING(void);
void cmdCORRECT(void);
void cmdWRONG(void);
void cmdSPEAKING(void);
void cmdSTOP(void);
void sendResponse(const char* response);
void parseAndSetTime(String timeData);

// ================================
// SETUP
// ================================

void setup() {
  // Initialize serial communication at 115200 baud for debugging and commands
  Serial.begin(115200);
  delay(1000);  // Allow serial to stabilize

  Serial.println("\n========================================");
  Serial.println("  Lumi Robot - Offline Learning Companion");
  Serial.println("  ESP32 Firmware Starting...");
  Serial.println("========================================\n");

  // Initialize all hardware subsystems with error handling
  setupHardware();

  Serial.println("\nLumi Robot Ready.");
  Serial.println("Type HELP for available commands.\n");

  systemInitialized = true;
}

void setupHardware(void) {
  Serial.println("[INIT] Setting up all hardware subsystems...\n");

  // --- Push Button ---
  // Must be initialized first as it doesn't depend on other peripherals
  setupButton();

  // --- I2S Audio (Microphone + Speaker) ---
  // Microphone must initialize first to detect audio input capability
  setupMicrophone();
  setupSpeaker();

  // --- RTC ---
  // Initialize RTC for timekeeping
  setupRTC();

  // --- SD Card ---
  // Initialize SD card for audio file storage
  setupSDCard();

  Serial.println("\n[INIT] All hardware subsystems initialized.");
}

// ================================
// MICROPHONE SETUP (INMP441 via I2S0)
// ================================
void setupMicrophone(void) {
  Serial.println("[MIC] Initializing INMP441 I2S microphone...");

  // Configure I2S0 for microphone input
  // The INMP441 is a digital I2S microphone
  // ESP32 acts as I2S master, providing clock signals

  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),  // Receive mode (input from mic)
    .sample_rate = SAMPLE_RATE,                             // 32kHz sample rate
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,           // 32-bit samples (INMP441 native)
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,            // Mono - left channel only
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,      // Standard I2S format
    .intr_alloc_flags = 0,                                  // Default interrupt priority
    .dma_buf_count = 4,                                     // Number of DMA buffers
    .dma_buf_len = BUFFER_SIZE,                             // Length of each DMA buffer
    .use_apll = false,                                      // Use APLL for clock
    .tx_desc_auto_clear = false,                            // Don't auto-clear TX descriptors
    .fixed_mclk = 0                                         // No fixed MCLK
  };

  // Assign I2S0 pins
  i2s_pin_config_t pin_config = {
    .mck_io_num = -1,         // No MCK pin (not needed)
    .bck_io_num  = MIC_BCK_PIN,  // BCK/SCK pin
    .ws_io_num   = MIC_WS_PIN,   // WS/LRCK pin
    .data_out_num = -1,        // Not used (input only)
    .data_in_num  = MIC_DATA_PIN  // Data input from microphone
  };

  // Install I2S driver on I2S0
  esp_err_t err = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  if (err != ESP_OK) {
    Serial.println("[ERROR] Failed to initialize microphone (I2S0 install failed).");
    Serial.println("[ERROR] Check wiring and ensure INMP441 is properly connected.");
    Serial.println("[ERROR] Error code: ");
    Serial.println(err);
    return;
  }

  // Configure I2S0 pins
  err = i2s_set_pin(I2S_NUM_0, &pin_config);
  if (err != ESP_OK) {
    Serial.println("[ERROR] Failed to set microphone I2S pins.");
    i2s_driver_uninstall(I2S_NUM_0);
    return;
  }

  Serial.println("[MIC] INMP441 microphone initialized successfully.");
  Serial.println("[MIC] Pins: BCK=GPIO14, WS=GPIO15, DATA=GPIO32");
}

// ================================
// SPEAKER SETUP (MAX98357A via I2S1)
// ================================
void setupSpeaker(void) {
  Serial.println("[SPK] Initializing MAX98357A I2S speaker...");

  // Configure I2S1 for speaker output
  // The MAX98357A is an I2S Class D amplifier
  // ESP32 acts as I2S master, sending audio data to the amplifier

  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),  // Transmit mode (output to speaker)
    .sample_rate = SAMPLE_RATE,                            // 32kHz sample rate
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,          // 32-bit samples
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,           // Mono - left channel only
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,     // Standard I2S format
    .intr_alloc_flags = 0,                                  // Default interrupt priority
    .dma_buf_count = 4,                                     // Number of DMA buffers
    .dma_buf_len = BUFFER_SIZE,                             // Length of each DMA buffer
    .use_apll = false,                                      // Use APLL for clock
    .tx_desc_auto_clear = true,                             // Auto-clear TX descriptors on empty
    .fixed_mclk = 0                                         // No fixed MCLK
  };

  // Assign I2S1 pins
  i2s_pin_config_t pin_config = {
    .mck_io_num = -1,           // No MCK pin
    .bck_io_num  = SPEAKER_BCK_PIN,  // BCK/SCK pin
    .ws_io_num   = SPEAKER_WS_PIN,   // WS/LRCK pin
    .data_out_num = SPEAKER_DATA_PIN, // Data output to MAX98357A
    .data_in_num  = -1         // Not used (output only)
  };

  // Install I2S driver on I2S1
  esp_err_t err = i2s_driver_install(I2S_NUM_1, &i2s_config, 0, NULL);
  if (err != ESP_OK) {
    Serial.println("[ERROR] Failed to initialize speaker (I2S1 install failed).");
    Serial.println("[ERROR] Check wiring and ensure MAX98357A is properly connected.");
    Serial.println("[ERROR] Error code: ");
    Serial.println(err);
    return;
  }

  // Configure I2S1 pins
  err = i2s_set_pin(I2S_NUM_1, &pin_config);
  if (err != ESP_OK) {
    Serial.println("[ERROR] Failed to set speaker I2S pins.");
    i2s_driver_uninstall(I2S_NUM_1);
    return;
  }

  // Mute the speaker initially
  i2s_zero_dma_buffer(I2S_NUM_1);

  Serial.println("[SPK] MAX98357A speaker initialized successfully.");
  Serial.println("[SPK] Pins: BCK=GPIO25, WS=GPIO26, DATA=GPIO27");
}

// ================================
// RTC SETUP (DS3231 via I2C)
// ================================
void setupRTC(void) {
  Serial.println("[RTC] Initializing DS3231 RTC...");

  Wire.begin(RTC_SDA_PIN, RTC_SCL_PIN);  // Initialize I2C with custom pins

  if (!rtc.begin()) {
    Serial.println("[ERROR] Failed to initialize DS3231 RTC.");
    Serial.println("[ERROR] Check wiring (SDA=GPIO21, SCL=GPIO22) and power.");
    rtcInitialized = false;
    return;
  }

  rtcInitialized = true;

  // Check if RTC lost power and set default time if needed
  if (rtc.lostPower()) {
    Serial.println("[RTC] WARNING: RTC lost power. Setting time to compile date.");
    // Set a default time - user can update it with SET_TIME command.
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }

  // Verify RTC time is reasonable.
  DateTime now = rtc.now();
  if (now.year() < 2020) {
    Serial.println("[RTC] WARNING: RTC time appears invalid. Setting default time.");
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    now = rtc.now();
  }

  Serial.println("[RTC] DS3231 initialized successfully.");
  Serial.print("[RTC] Current time: ");
  Serial.print(now.year(), DEC);
  Serial.print('-');
  Serial.print(now.month(), DEC);
  Serial.print('-');
  Serial.print(now.day(), DEC);
  Serial.print(' ');
  Serial.print(now.hour(), DEC);
  Serial.print(':');
  Serial.print(now.minute(), DEC);
  Serial.print(':');
  Serial.println(now.second(), DEC);
}

// ================================
// SD CARD SETUP (via SPI)
// ================================
void setupSDCard(void) {
  Serial.println("[SD] Initializing MicroSD card...");

  // Configure SPI pins explicitly
  SPI.begin(SD_SCK_PIN, SD_MISO_PIN, SD_MOSI_PIN, SD_CS_PIN);

  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("[ERROR] Failed to initialize SD card.");
    Serial.println("[ERROR] Check card insertion and wiring (CS=GPIO5, MOSI=GPIO23, MISO=GPIO19, SCK=GPIO18).");
    Serial.println("[ERROR] Ensure an 8GB or smaller FAT32 formatted card is inserted.");
    return;
  }

  // Verify card type and size
  uint8_t cardType = SD.cardType();
  if (cardType == CARD_NONE) {
    Serial.println("[ERROR] No SD card detected.");
    return;
  }

  uint64_t cardSize = SD.cardSize() / (1024 * 1024);
  Serial.print("[SD] SD card initialized successfully.");
  Serial.print(" Type: ");
  switch (cardType) {
    case CARD_MMC:   Serial.print("MMC"); break;
    case CARD_SD:    Serial.print("SDSC"); break;
    case CARD_SDHC:  Serial.print("SDHC"); break;
    default:         Serial.print("UNKNOWN"); break;
  }
  Serial.print(" Size: ");
  Serial.print(cardSize);
  Serial.println(" MB");

  // List files if available
  Serial.println("[SD] Root directory contents:");
  File root = SD.open("/");
  if (root) {
    File entry = root.openNextFile();
    while (entry) {
      if (entry.isDirectory()) {
        Serial.print("  [DIR]  ");
        Serial.println(entry.name());
      } else {
        Serial.print("  [FILE] ");
        Serial.print(entry.name());
        Serial.print(" (");
        Serial.print(entry.size());
        Serial.println(" bytes)");
      }
      entry = root.openNextFile();
    }
    root.close();
  }
}

// ================================
// BUTTON SETUP
// ================================
void setupButton(void) {
  // Configure push button pin with internal pull-up
  // Button connects between GPIO and GND (active LOW)
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  Serial.println("[BTN] Push button initialized on GPIO33.");
}

// ================================
// BUTTON HANDLING
// ================================
// Check if the button is pressed with debounce
// Returns true only on a new press edge (not while held)
bool isButtonPressed(void) {
  if (!buttonEnabled) {
    return false;  // Button functionality disabled
  }

  int reading = digitalRead(BUTTON_PIN);

  // Button is active LOW (pressing connects pin to GND)
  if (reading == LOW) {
    unsigned long currentTime = millis();
    // Debounce: only register a new press if enough time has passed
    if (currentTime - lastButtonTime > BUTTON_DEBOUNCE_MS) {
      lastButtonTime = currentTime;
      return true;  // New button press detected
    }
  }

  return false;
}

// ================================
// I2S AUDIO FUNCTIONS
// ================================

// Read audio data from the microphone via I2S
// Returns number of bytes read, or -1 on error
int readMicrophone(void) {
  size_t bytesRead = 0;
  esp_err_t err = i2s_read(I2S_NUM_0, i2s_rx_buffer, sizeof(i2s_rx_buffer), &bytesRead, portMAX_DELAY);
  if (err != ESP_OK) {
    return -1;
  }
  return (int)bytesRead;
}

// Play audio data through the speaker via I2S
// data: pointer to audio buffer
// length: number of bytes to write
// Returns true on success
bool playAudio(const uint8_t* data, size_t length) {
  size_t bytesWritten = 0;
  esp_err_t err = i2s_write(I2S_NUM_1, data, length, &bytesWritten, portMAX_DELAY);
  if (err != ESP_OK) {
    Serial.println("[SPK] Error writing audio to speaker.");
    return false;
  }
  return (bytesWritten == length);
}

// Play silence through the speaker
void playSilence(void) {
  i2s_zero_dma_buffer(I2S_NUM_1);
}

// ================================
// SERIAL COMMAND HANDLER
// ================================

// Process incoming serial commands
void handleSerialCommands(void) {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove whitespace and newlines
    command.toUpperCase();  // Normalize to uppercase
    processCommand(command);
  }
}

// Route commands to appropriate handlers
void processCommand(String command) {
  if (command == "PING") {
    cmdPING();
  } else if (command == "HELP") {
    cmdHELP();
  } else if (command == "STATUS") {
    cmdSTATUS();
  } else if (command == "GET_TIME") {
    cmdGET_TIME();
  } else if (command.startsWith("SET_TIME")) {
    cmdSET_TIME(command);
  } else if (command == "MIC_TEST") {
    cmdMIC_TEST();
  } else if (command == "SD_STATUS") {
    cmdSD_STATUS();
  } else if (command == "SD_LIST") {
    cmdSD_LIST();
  } else if (command == "LISTENING") {
    cmdLISTENING();
  } else if (command == "THINKING") {
    cmdTHINKING();
  } else if (command == "CORRECT") {
    cmdCORRECT();
  } else if (command == "WRONG") {
    cmdWRONG();
  } else if (command == "SPEAKING") {
    cmdSPEAKING();
  } else if (command == "STOP") {
    cmdSTOP();
  } else {
    Serial.println("ERROR:UNKNOWN_COMMAND");
  }
}

// ================================
// COMMAND IMPLEMENTATIONS
// ================================

// PING → PONG
void cmdPING(void) {
  Serial.println("PONG");
}

// HELP → List all available commands
void cmdHELP(void) {
  Serial.println("Available commands:");
  Serial.println("  PING        - Test connection");
  Serial.println("  HELP        - Show this help message");
  Serial.println("  STATUS      - Show system status");
  Serial.println("  GET_TIME    - Get current RTC time");
  Serial.println("  SET_TIME    - Set RTC time (use format: SET_TIME YYYY-MM-DD HH:MM:SS)");
  Serial.println("  MIC_TEST    - Run microphone test");
  Serial.println("  SD_STATUS   - Show SD card status");
  Serial.println("  SD_LIST     - List files on SD card");
  Serial.println("  LISTENING   - Enter listening mode");
  Serial.println("  THINKING    - Enter thinking mode");
  Serial.println("  CORRECT     - Signal correct response");
  Serial.println("  WRONG       - Signal wrong response");
  Serial.println("  SPEAKING    - Begin audio playback");
  Serial.println("  STOP        - Stop all audio");
}

// STATUS → STATUS:READY
void cmdSTATUS(void) {
  Serial.println("STATUS:READY");
}

// GET_TIME → TIME:YYYY-MM-DD HH:MM:SS
void cmdGET_TIME(void) {
  if (!rtcInitialized) {
    Serial.println("ERROR:RTC_NOT_INITIALIZED");
    return;
  }
  DateTime now = rtc.now();
  char timeStr[20];
  snprintf(timeStr, sizeof(timeStr), "TIME:%04d-%02d-%02d %02d:%02d:%02d",
           now.year(), now.month(), now.day(),
           now.hour(), now.minute(), now.second());
  Serial.println(timeStr);
}

// SET_TIME - Set RTC time from a complete serial command
// Format: SET_TIME YYYY-MM-DD HH:MM:SS
void cmdSET_TIME(String command) {
  if (!rtcInitialized) {
    Serial.println("ERROR:RTC_NOT_INITIALIZED");
    return;
  }

  // Remove the command name and keep only the timestamp.
  command.trim();
  if (command.length() < 8) {
    Serial.println("ERROR:INVALID_TIME_FORMAT");
    Serial.println("Use: SET_TIME YYYY-MM-DD HH:MM:SS");
    return;
  }

  String timeStr = command.substring(8);
  timeStr.trim();

  if (timeStr.length() < 19) {
    Serial.println("ERROR:INVALID_TIME_FORMAT");
    Serial.println("Use: SET_TIME YYYY-MM-DD HH:MM:SS");
    return;
  }

  int year   = timeStr.substring(0, 4).toInt();
  int month  = timeStr.substring(5, 7).toInt();
  int day    = timeStr.substring(8, 10).toInt();
  int hour   = timeStr.substring(11, 13).toInt();
  int minute = timeStr.substring(14, 16).toInt();
  int second = timeStr.substring(17, 19).toInt();

  if (year < 2020 ||
      month < 1 || month > 12 ||
      day < 1 || day > 31 ||
      hour < 0 || hour > 23 ||
      minute < 0 || minute > 59 ||
      second < 0 || second > 59 ||
      timeStr.charAt(4) != '-' ||
      timeStr.charAt(7) != '-' ||
      timeStr.charAt(10) != ' ' ||
      timeStr.charAt(13) != ':' ||
      timeStr.charAt(16) != ':') {
    Serial.println("ERROR:INVALID_TIME_VALUE");
    return;
  }

  DateTime newTime(year, month, day, hour, minute, second);
  rtc.adjust(newTime);
  Serial.println("TIME_SET:OK");
}

// MIC_TEST - Test microphone by reading samples
void cmdMIC_TEST(void) {
  Serial.println("MIC_TEST:STARTING");
  Serial.println("Reading 10 samples from microphone...");

  int successCount = 0;
  int failCount = 0;

  for (int i = 0; i < 10; i++) {
    int bytesRead = readMicrophone();
    if (bytesRead > 0) {
      successCount++;
      // Calculate approximate RMS of the audio samples
      uint32_t sum = 0;
      for (int j = 0; j < bytesRead; j += 4) {
        int32_t sample = (int32_t)(i2s_rx_buffer[j] | (i2s_rx_buffer[j+1] << 8) |
                                    (i2s_rx_buffer[j+2] << 16) | (i2s_rx_buffer[j+3] << 24));
        sum += sample * sample;
      }
      float rms = sqrt((float)sum / (bytesRead / 4));
      Serial.print("Sample ");
      Serial.print(i + 1);
      Serial.print(": bytes=");
      Serial.print(bytesRead);
      Serial.print(" RMS=");
      Serial.println(rms, 0);
    } else {
      failCount++;
      Serial.print("Sample ");
      Serial.print(i + 1);
      Serial.println(": FAILED (no data)");
    }
    delay(10);
  }

  Serial.print("MIC_TEST:RESULT - Success: ");
  Serial.print(successCount);
  Serial.print("/10, Failures: ");
  Serial.println(failCount);

  if (successCount >= 8) {
    Serial.println("MIC_STATUS:OK");
  } else {
    Serial.println("MIC_STATUS:POOR");
  }
}

// SD_STATUS - Show SD card status
void cmdSD_STATUS(void) {
  if (SD.cardType() == CARD_NONE) {
    Serial.println("SD_STATUS:NO_CARD");
    return;
  }

  uint64_t cardSize = SD.cardSize() / (1024 * 1024);
  Serial.print("SD_STATUS:OK Size=");
  Serial.print(cardSize);
  Serial.println("MB");
}

// SD_LIST - List all files on SD card
void cmdSD_LIST(void) {
  if (SD.cardType() == CARD_NONE) {
    Serial.println("SD_LIST:NO_CARD");
    return;
  }

  Serial.println("SD_FILES:");
  File root = SD.open("/");
  if (root) {
    File entry = root.openNextFile();
    while (entry) {
      if (entry.isDirectory()) {
        Serial.print("  [DIR]  ");
        Serial.println(entry.name());
      } else {
        Serial.print("  [FILE] ");
        Serial.print(entry.name());
        Serial.print(" (");
        Serial.print(entry.size());
        Serial.println(" bytes)");
      }
      entry = root.openNextFile();
    }
    root.close();
  }
  Serial.println("SD_LIST:END");
}

// LISTENING - Enter listening mode
void cmdLISTENING(void) {
  listeningMode = true;
  thinkingMode = false;
  speakingMode = false;
  Serial.println("MODE:LISTENING");
  Serial.println("[MODE] Listening mode active. Speak into the microphone.");
}

// THINKING - Enter thinking mode
void cmdTHINKING(void) {
  listeningMode = false;
  thinkingMode = true;
  speakingMode = false;
  Serial.println("MODE:THINKING");
  Serial.println("[MODE] Thinking mode active.");
}

// CORRECT - Signal correct response (plays a short beep)
void cmdCORRECT(void) {
  Serial.println("FEEDBACK:CORRECT");
  // Play a short confirmation tone (approximately 1000Hz for 200ms)
  Serial.println("[AUDIO] Playing correct tone.");
  // Generate simple tone pattern - 1000Hz sine approximation
  uint32_t toneLen = SAMPLE_RATE / 1000 * 200 / 4;  // ~200ms worth of 32-bit samples
  for (uint32_t i = 0; i < toneLen && i < (AUDIO_BLOCK_SIZE / 4); i++) {
    // Simple square wave approximation for quick feedback
    int32_t sample = (i % 16 < 8) ? 2147483647 : -2147483648;  // Simple square wave
    i2s_write(I2S_NUM_1, &sample, 4, NULL, 0);
  }
  delay(250);
  playSilence();
}

// WRONG - Signal wrong response (plays a low tone)
void cmdWRONG(void) {
  Serial.println("FEEDBACK:WRONG");
  Serial.println("[AUDIO] Playing wrong tone.");
  // Generate lower frequency tone for wrong feedback
  uint32_t toneLen = SAMPLE_RATE / 1000 * 300 / 4;  // ~300ms
  for (uint32_t i = 0; i < toneLen && i < (AUDIO_BLOCK_SIZE / 4); i++) {
    int32_t sample = (i % 32 < 16) ? 2147483647 : -2147483648;
    i2s_write(I2S_NUM_1, &sample, 4, NULL, 0);
  }
  delay(350);
  playSilence();
}

// SPEAKING - Begin audio playback from SD card
void cmdSPEAKING(void) {
  speakingMode = true;
  listeningMode = false;
  thinkingMode = false;
  Serial.println("MODE:SPEAKING");
  Serial.println("[AUDIO] Begin speaking. Check SD card for audio files.");

  // Try to play an audio file if one exists
  // This demonstrates reading audio from SD card
  if (SD.cardType() != CARD_NONE) {
    File root = SD.open("/");
    File entry = root.openNextFile();
    bool foundAudio = false;

    while (entry) {
      if (!entry.isDirectory() && String(entry.name()).endsWith(".wav")) {
        Serial.print("[AUDIO] Playing: ");
        Serial.println(entry.name());
        audioFile = entry;
        foundAudio = true;
        break;
      }
      entry = root.openNextFile();
    }
    root.close();

    if (!foundAudio) {
      Serial.println("[AUDIO] No .wav files found on SD card.");
      Serial.println("[AUDIO] Place audio files in root directory of SD card.");
    }
  } else {
    Serial.println("[AUDIO] SD card not available for playback.");
  }
}

// STOP - Stop all audio and modes
void cmdSTOP(void) {
  listeningMode = false;
  thinkingMode = false;
  speakingMode = false;
  playSilence();
  if (audioFile) {
    audioFile.close();
    audioFile = File();
  }
  Serial.println("MODE:STOPPED");
  Serial.println("[AUDIO] All audio stopped.");
}

// ================================
// HELPER FUNCTIONS
// ================================

// Send a response string over serial
void sendResponse(const char* response) {
  Serial.println(response);
}

// Read and parse the time string for SET_TIME
// This is called when the full SET_TIME command with timestamp arrives in one line
void parseAndSetTime(String timeData) {
  // Time data format: "YYYY-MM-DD HH:MM:SS"
  if (timeData.length() >= 19) {
    int year = timeData.substring(0, 4).toInt();
    int month = timeData.substring(5, 7).toInt();
    int day = timeData.substring(8, 10).toInt();
    int hour = timeData.substring(11, 13).toInt();
    int minute = timeData.substring(14, 16).toInt();
    int second = timeData.substring(17, 19).toInt();
    rtc.adjust(DateTime(year, month, day, hour, minute, second));
    Serial.println("TIME_SET:OK");
  } else {
    Serial.println("ERROR:INVALID_TIME_FORMAT");
  }
}

// ================================
// MAIN LOOP
// ================================
void loop() {
  // Handle serial commands
  handleSerialCommands();

  // Check for button press
  if (isButtonPressed()) {
    Serial.println("[BTN] Button pressed!");
    // Toggle speaking mode on button press
    if (!speakingMode) {
      cmdSPEAKING();
    } else {
      cmdSTOP();
    }
  }

  // In listening mode, continuously read from microphone
  if (listeningMode) {
    int bytesRead = readMicrophone();
    if (bytesRead > 0) {
      // Audio detected - this data can be processed by the learning algorithm
      // Currently just monitoring for activity
      // The raw PCM data is in i2s_rx_buffer
      (void)bytesRead;  // Suppress unused variable warning
    }
    yield();  // Allow other tasks to run (ESP32 cooperative multitasking)
  }
}
// ================================================================
// End of Lumi_Robot.ino
// ================================================================