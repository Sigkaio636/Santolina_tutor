// Santolina: the board's Wi-Fi status on the 8x13 LED matrix.
// Python sets the mode with Bridge.call("set_mode", n); the animations run here, so they stay
// smooth whatever Linux is doing. Nothing flashes more than 3 times a second.
//   0 off        the board's Wi-Fi is off: the matrix stays dark
//   1 waiting    the Wi-Fi is on, waiting for a phone: the Wi-Fi symbol's arcs grow from the dot
//   2 connected  a phone joined: a check mark draws itself, then bounces gently

#include <Arduino_RouterBridge.h>
#include <Arduino_LED_Matrix.h>

Arduino_LED_Matrix matrix;

const uint8_t ROWS = 8;
const uint8_t COLS = 13;
uint8_t frame[ROWS * COLS];

volatile int mode = 0;
int shownMode = -1;
unsigned long modeSince = 0;

// Each shape is a list of (row, column) pixels.
struct Pixel { uint8_t r, c; };

const Pixel WIFI_DOT[] = {{7, 6}};
const Pixel WIFI_ARC1[] = {{4, 5}, {4, 6}, {4, 7}, {5, 4}, {5, 8}};
const Pixel WIFI_ARC2[] = {{2, 4}, {2, 5}, {2, 6}, {2, 7}, {2, 8}, {3, 3}, {3, 9}};
const Pixel WIFI_ARC3[] = {{0, 3}, {0, 4}, {0, 5}, {0, 6}, {0, 7}, {0, 8}, {0, 9},
                           {1, 2}, {1, 10}, {2, 1}, {2, 11}};
// The check mark, in drawing order: down the short stroke, then up the long one.
const Pixel CHECK[] = {{4, 1}, {5, 2}, {6, 3}, {7, 4}, {6, 5}, {5, 6}, {4, 7}, {3, 8}, {2, 9},
                       {1, 10}};

#define LEN(a) (sizeof(a) / sizeof(a[0]))

void clearFrame() { memset(frame, 0, sizeof(frame)); }

void put(const Pixel *shape, size_t n, uint8_t level, int dy = 0) {
  for (size_t i = 0; i < n; i++) {
    int r = shape[i].r + dy;
    if (r >= 0 && r < ROWS) frame[r * COLS + shape[i].c] = level;
  }
}

// Waiting: the dot stays on; arcs appear one by one, the newest brightest. 4 steps of 450 ms.
void drawWaiting(unsigned long t) {
  int step = (t / 450) % 5;  // 0: dot, 1: +arc1, 2: +arc2, 3: +arc3, 4: all, dimmer
  clearFrame();
  put(WIFI_DOT, LEN(WIFI_DOT), 7);
  if (step >= 1) put(WIFI_ARC1, LEN(WIFI_ARC1), step == 1 ? 7 : 4);
  if (step >= 2) put(WIFI_ARC2, LEN(WIFI_ARC2), step == 2 ? 7 : 3);
  if (step >= 3) put(WIFI_ARC3, LEN(WIFI_ARC3), step == 3 ? 7 : 2);
}

// Connected: the check mark draws itself pixel by pixel, then bounces one row every 600 ms.
void drawConnected(unsigned long t) {
  clearFrame();
  size_t drawn = t / 70;
  if (drawn < LEN(CHECK)) {
    put(CHECK, drawn + 1, 7);
    return;
  }
  int dy = ((t - LEN(CHECK) * 70) / 600) % 2 ? -1 : 0;
  put(CHECK, LEN(CHECK), 7, dy);
}

void set_mode(int newMode) { mode = newMode; }

void setup() {
  matrix.begin();
  matrix.setGrayscaleBits(3);  // brightness 0 to 7
  matrix.clear();
  clearFrame();
  Bridge.begin();
  Bridge.provide("set_mode", set_mode);
}

void loop() {
  int m = mode;
  if (m != shownMode) {
    shownMode = m;
    modeSince = millis();
  }
  unsigned long t = millis() - modeSince;
  if (m == 1) drawWaiting(t);
  else if (m == 2) drawConnected(t);
  else clearFrame();
  matrix.draw(frame);
  delay(20);
}
