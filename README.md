# ChroMod

A small patch for ModRetro Chromatic CLI 1.2.1 on Apple Silicon Macs. It removes the `rom.released_title_denied` block so ROM writing can proceed.

`patch.py` changes one instruction in a copy of the original binary and signs it locally. You then use **the patched CLI** to flash: Python only prepares the executable.

You need **Python 3.10+**, `codesign`, a Chromatic connected over USB with **Developer Mode already enabled**, and a compatible rewritable cartridge. Writing has been tested on a ModRetro Demo Cartridge.

From the project folder:

1. Download the original binary (once).

   ```sh
   mkdir -p vendor
   curl -fL 'https://registry.npmjs.org/@modretro/chromatic-cli-darwin-arm64/-/chromatic-cli-darwin-arm64-1.2.1.tgz' | tar -xzO package/bin/chromatic-cli > vendor/chromatic-cli-1.2.1-macos-arm64
   ```

2. Apply the patch (once).

   ```sh
   python3 patch.py
   ```

   This creates `build/chromatic-cli` and keeps the original intact. No extra Python packages needed.

3. Flash a game, replacing the path with your ROM’s location.

   **This command overwrites the game on the cartridge.**

   ```sh
   ./build/chromatic-cli write-homebrew '/path/to/game.gb' --player 1
   ```

   Once writing completes successfully, restart the Chromatic:

   ```sh
   ./build/chromatic-cli reset-device --player 1
   ```

For another game, just repeat step 3. `--player 1` selects the device assigned Player 1.

The patch replaces `b.eq` with `nop` at offset `0x2B780`; it only works with the expected binary, checked using SHA-256. It does not enable Developer Mode or permanently unlock the cartridge. This project includes no ROMs or original ModRetro source code.
