# ScoopOS Bow Wow: Agent Masterclass presentation
**Monday, October 12, 2026 · 4 PM Arizona · 26:35 timed interactive lesson**

**SHARE THIS WINDOW IN ZOOM (slides only, no notes):** https://scoopos-bowwow-masterclass.markgromer.workers.dev/?audience=1

**Slide navigation page (also notes-free):** https://scoopos-bowwow-masterclass.markgromer.workers.dev/

**Speaker-notes view:** https://scoopos-bowwow-masterclass.markgromer.workers.dev/?presenter=1

**One-page member handout:** https://scoopos-bowwow-masterclass.markgromer.workers.dev/?handout=1

## How to present
1. Open the dedicated [Audience Window](https://scoopos-bowwow-masterclass.markgromer.workers.dev/?audience=1) in a **separate browser window**. This shows only the 16:9 slides, with no presenter notes, toolbars or controls.
2. Open the [Private Presenter Console](https://scoopos-bowwow-masterclass.markgromer.workers.dev/?presenter=1) in another window or on a second monitor. This shows your speaking notes, pacing, navigation and next slide. It has an unmistakable PRIVATE warning.
3. In Zoom choose **Share → Window**, and select **only the Audience Window**. Do **not** share the entire desktop/monitor while notes are visible. If you accidentally share the presenter window, the audience WILL see your notes.
4. Navigate from your presenter console: slide changes sync to the Audience Window through the same-browser-session BroadcastChannel/local storage. Keep both windows open.
5. Press **Right Arrow / Space** to advance, **Left** to return, **R** for the resource hub, **F** for fullscreen, **P** to open presenter mode.
6. Press **Start timer** when you begin. The full run-of-show is 26:35 plus optional questions.
7. On live-build slides, open the [Agent Lab](https://scoopos-agent-lab.markgromer.workers.dev/) and have members build alongside you. Use only approved or fictional information.
8. For the real integration demonstration follow [LIVE-DEMO.md](../LIVE-DEMO.md). The seeded Airtable demo records are fictional and the underlying connector read/write has been tested, but the full Work agent is a separate end-to-end test.
9. Conclude with three tests: real source, unknown fact, human approval. Share the [handout](https://scoopos-bowwow-masterclass.markgromer.workers.dev/?handout=1).

## Design
- 16 visual, editorial, 16:9 slide scenes, rendered on a fixed intrinsic 1600×900 canvas and scaled as one unit to avoid clipping in the small presenter thumbnail.
- Interactive job-selection and safe-answer reveal, rather than a quiz that pretends to build an agent.
- Dedicated synchronized presenter window, slide pacing, elapsed timer, full screen, keyboard navigation, and an all-links resource hub.
- Printable student handout; no attendee data is collected.
- No proprietary assets, fonts, externally required JS frameworks, or student API keys in the deck. QR image requires the public QR service; the clickable lab link is always displayed.

## Architecture
`index.html` is the entire source. Deployed to a standalone Cloudflare Worker (not replacing the main Agent Lab).

The old beginner quiz is obsolete and redirects to the real Agent Lab. This deck is the lesson that precedes the Lab build.
