# Original panel assets for the optional emulator

These files are **host-side inputs only**. Enabling the emulator never uploads
them, changes the LCD's font/icon library or modifies the managed atlases.

- `9.ICO`: the stock library supplied for this project; original 256-entry,
  16-byte directory and embedded JPEG payloads are retained, including holes.
- `0_DWIN_ASC.HZK`: the developer-supplied file, downloaded unchanged from
  [ihrapsa/T5UIC1-DWIN-toolset](https://github.com/ihrapsa/T5UIC1-DWIN-toolset/blob/main/Dwin_Toolbox-en%2F0_DWIN_ASC.HZK).
  It is a **DGUS** ASCII library: 128 glyphs per bank, widths 4..64,
  height twice the width. It is retained and can be selected explicitly.
- `0T5UIC1.HZK`: default T5UIC1 original font from
  [Quint097/DWIN_Font_Tools](https://github.com/Quint097/DWIN_Font_Tools/blob/main/HZK%20Font%20Files/DWIN%20Font%20(Original)/0T5UIC1.HZK).
  The native ASCII banks use widths 6, 8, 10, 12, 14, 16, 20, 24, 28, 32;
  each has 128 glyphs and MSB-first, byte-aligned rows.
  Layout references: [upstream decoder](https://github.com/Quint097/DWIN_Font_Tools/blob/main/HZK%20Font%20Decoder/src/decode.go)
  and [Marlin font generator](https://github.com/MarlinFirmware/Marlin/blob/2.1.x/buildroot/share/fonts/buildhzk.py).

Upstream assets retain their original provenance; this project does not claim
authorship of these binary files. Match the selected font and 9.ICO to the
files installed on your physical panel when comparing screenshots.
