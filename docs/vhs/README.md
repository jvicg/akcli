# VHS Automated Recordings

This directory contains [VHS](https://github.com/charmbracelet/vhs) tape scripts used to automatically generate the GIF recordings shown in the documentation.

To avoid exposing sensitive credentials and to ensure the GIFs are deterministic, we use a dummy HTTPS server to process the requests instead of the real Akamai API.

This script:

1. **Prevents Data Leaks:** It completely isolates the recording environment so no real Akamai API tokens or sensitive production data are leaked into the repository or the GIFs.
2. **Reuses Test Infrastructure:** It spins up the exact same dummy HTTPS server used in our integration tests (`tests/fixtures/https_server.py`).
3. **Mocks Answers:** It intercepts the requests made by the CLI during the `vhs` execution and serves pre-configured dummy responses, allowing us to safely simulate real API behavior.
    All the dummy responses are located at (`tests/fixtures/data`). Since answers are mocked, the server is only configured to answer to certain requests. Check out the server script to how
    it's configured.

---

### Configuration

Global tapes configuration (theming, padding, font size, etc.) is controlled in `config.tape`.

---

### Generate GIFS

To spin up the dummy server and generate the full list of GIFs sequentially, run:

```bash
python generate.py
```

Make sure you have `vhs` installed and located in your PATH.
