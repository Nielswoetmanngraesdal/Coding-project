# Phase 2 Runtime Documentation

**Phase 2: Architecture and Design Documentation**

---

## 1. What Was Created

### New/Updated Documentation
- `docs/concepts.md`
  - System overview (Trigger, Observer, Control, Response)
  - MQTT architecture (topics, publishers/subscribers, JSON schemas)
  - Configuration parameters for `config.yaml`
  - Architecture decisions (notebooks, library code, classes vs functions)
  - Open questions and assumptions

### Code Changes
- None in this phase (documentation-only).

### Configuration Changes
- None in this phase.
- Required keys are documented in `docs/concepts.md` for implementation phases.

---

## 2. How to Run (Phase 2 Validation Workflow)

1. Open `docs/concepts.md`.
2. Verify these sections exist:
   - System Overview
   - MQTT Architecture
   - Configuration Parameters
   - Architecture Decisions
   - Open Questions
3. Run validation from project root:
   - `python scripts/verify_setup.py`
   - `python scripts/validate_structure.py`
   - `python -m pytest`
4. Confirm no regressions from previous phases.

---

## 3. Expected Output

### A) Manual documentation check
- `docs/concepts.md` exists.
- All required headings are present.
- MQTT topics and JSON schemas are documented.
- Config keys and defaults are listed.

If a section is missing, Phase 2 is incomplete.

### B) `python scripts/verify_setup.py`
Expected:
- Environment/dependency checks pass.
- No fatal errors.

If it fails:
- Install dependencies:
  - `pip install -e ".[dev,notebooks]"`

### C) `python scripts/validate_structure.py`
Expected:
- Structure checks pass.
- No forbidden patterns are reported.

If it fails:
- Align files with `.github/copilot-instructions.md`.

### D) `python -m pytest`
Expected:
- Existing tests pass.
- Some skips are acceptable (for optional runtime services).

If failures occur:
- Fix regressions before starting the next phase.

---

## 4. MQTT Topics (Documented Contracts)

- `city/flood/trigger`
  - **Publisher:** Trigger agent
  - **Subscribers:** Control agent, Dashboard
  - **Schema:**
    ```json
    {
      "event": "rain|dam_break",
      "severity": "low|high",
      "timestamp": "ISO-8601 string"
    }
    ```

- `city/flood/observer/<sensor_id>`
  - **Publisher:** Observer agent(s)
  - **Subscribers:** Control agent, Dashboard
  - **Schema:**
    ```json
    {
      "sensor_id": "string",
      "water_level": 0.0,
      "flow_rate": 0.0,
      "timestamp": "ISO-8601 string"
    }
    ```

- `city/flood/control/command`
  - **Publisher:** Control agent
  - **Subscribers:** Response agent, Dashboard
  - **Schema:**
    ```json
    {
      "action": "alert|activate_pump|close_gate",
      "target": "string",
      "parameters": {},
      "timestamp": "ISO-8601 string"
    }
    ```

- `city/flood/response/status`
  - **Publisher:** Response agent
  - **Subscribers:** Dashboard
  - **Schema:**
    ```json
    {
      "device": "string",
      "status": "string",
      "details": {},
      "timestamp": "ISO-8601 string"
    }
    ```

---

## 5. Debugging Guidance

- If Phase 2 appears incomplete:
  - Re-check `docs/concepts.md` headings and required subsections.
- If topic names differ across docs:
  - Standardize all names in `docs/concepts.md` now.
- If schema fields differ from planned dataclasses:
  - Align names before implementation to avoid parser errors.
- If assumptions are unclear:
  - Add explicit assumptions in the Open Questions section.

---

## 6. Verification Commands

Run from:
`c:\Users\Nille\OneDrive\Documents\GitHub\Coding-project`

```bash
python scripts/verify_setup.py
python scripts/validate_structure.py
python -m pytest
```

---

## Phase 2 Completion Criteria

Phase 2 is complete when:
- `docs/concepts.md` contains all required sections.
- MQTT contracts are consistent and clear.
- Validation commands run without new failures.
- No implementation code is added in this phase.