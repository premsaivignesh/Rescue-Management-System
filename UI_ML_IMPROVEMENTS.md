# UI and incident-level ML improvements

This build retains the dark charcoal, deep green, and olive palette and adds targeted usability fixes:

- Citizen dashboard recent reports now have an **Open** action that filters My Reports to the selected incident.
- My Reports cards have clearer separation using rounded panels, borders, and the established green palette.
- Incident details read persisted multimodal AI output from the database instead of always showing placeholder `Pending` labels.
- Per-incident details include saved incident/severity confidence, spam classification, people estimate, resource predictions, department, priority, AI review summary, and an embedded resource-demand bar chart when a saved result exists.
- Report Incident spacing between image and video controls is more compact.
- Returning from Department Login clears the previous widgets before rebuilding the citizen login page.
- Notification refresh actions use a branded, animated three-second rescue-themed loading overlay.

## Important ML interpretation

The incident-level charts display the saved prediction for that incident, not a claim of real-world certainty. The dataset used for training is synthetic/academic, and YOLO's COCO object detector identifies common objects; it does not diagnose injuries or independently detect medical severity. Older incidents created before AI output was persisted can legitimately show that their historical AI result is unavailable.

## Validation

`python -m compileall -q gui utils database ai_ml` completed successfully and `python -m pytest -q` passed the included test (`1 passed`). Run `python main.py` in the project's configured environment for GUI validation.
