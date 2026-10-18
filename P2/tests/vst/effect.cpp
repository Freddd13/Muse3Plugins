// SPDX-License-Identifier: GPL-2.0-or-later
// A small, deliberately delayed effect used to verify the host, never
// installed.
#include "aeffectx.h"
#include <array>
#include <cstdlib>
#include <cstring>
#include <windows.h>
struct Effect {
  AEffect api{};
  float gain = .5f;
  int at = 0;
  std::array<float, 32> left{}, right{};
  Effect() {
    api.magic = kEffectMagic;
    api.dispatcher = dispatch;
    api.setParameter = set;
    api.getParameter = get;
    api.numParams = 2;
    api.numInputs = api.numOutputs = 2;
    api.flags = effFlagsCanReplacing | (1 << 5);
    int delay = 32;
    std::memcpy(api.empty3, &delay, 4);
    api.uniqueID = 0x4b756d6f;
    api.processReplacing = process;
    api.ptr3 = this;
  }
  static Effect *self(AEffect *e) { return static_cast<Effect *>(e->ptr3); }
  static void set(AEffect *e, int index, float value) {
    if (index == 1 && value > .9f)
      ExitProcess(77);
    if (index == 0)
      self(e)->gain = value;
  }
  static float get(AEffect *e, int) { return self(e)->gain; }
  static intptr_t dispatch(AEffect *e, int32_t op, int32_t, intptr_t value,
                           void *pointer, float) {
    auto p = self(e);
    switch (op) {
    case effClose:
      delete p;
      return 1;
    case effGetEffectName:
      std::strcpy(static_cast<char *>(pointer), "Kumo delay test");
      return 1;
    case effGetVendorString:
      std::strcpy(static_cast<char *>(pointer), "Freddd13");
      return 1;
    case effGetProductString:
      std::strcpy(static_cast<char *>(pointer), "Kumo test effect");
      return 1;
    case effGetParamName:
      std::strcpy(static_cast<char *>(pointer), "Gain");
      return 1;
    case effGetChunk:
      *static_cast<void **>(pointer) = &p->gain;
      return sizeof(float);
    case effSetChunk:
      if (value == sizeof(float))
        std::memcpy(&p->gain, pointer, sizeof(float));
      return 1;
    case effCanDo:
      return 1;
    default:
      return 0;
    }
  }
  static void process(AEffect *e, float **in, float **out, int32_t count) {
    auto p = self(e);
    for (int i = 0; i < count; ++i) {
      out[0][i] = p->left[p->at] * p->gain;
      out[1][i] = p->right[p->at] * p->gain;
      p->left[p->at] = in[0][i];
      p->right[p->at] = in[1][i];
      p->at = (p->at + 1) % 32;
    }
  }
};
extern "C" __declspec(dllexport) AEffect *VSTPluginMain(audioMasterCallback) {
  return &(new Effect)->api;
}
