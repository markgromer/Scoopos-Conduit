# ScoopOS Bow Wow: Agent Masterclass presentation
**Monday, October 12, 2026 · 4 PM Arizona · 26:35 timed interactive lesson**

**Live screen-share deck:** https://scoopos-bowwow-masterclass.markgromer.workers.dev/

**Speaker-notes view:** https://scoopos-bowwow-masterclass.markgromer.workers.dev/?presenter=1

**One-page member handout:** https://scoopos-bowwow-masterclass.markgromer.workers.dev/?handout=1

## How to present
1. Share **only the normal deck window** in Zoom.
2. Open **Presenter** in a separate window or second screen. This view shows speaking notes, slide pace, the next slide, and the timed session. It syncs with the audience window.
3. Press **Right Arrow / Space** to advance, **Left** to return, **R** for the resource hub, **F** for fullscreen, **P** to open presenter mode.
4. Press **Start timer** when you begin. The full run-of-show is 26:35 plus optional questions.
5. On live-build slides, open the [Agent Lab](https://scoopos-agent-lab.markgromer.workers.dev/) and have members build alongside you. Use only approved or fictional information.
6. For the real integration demonstration follow [LIVE-DEMO.md](../LIVE-DEMO.md). The seeded Airtable demo records are fictional and the underlying connector read/write has been tested, but the full Work agent is a separate end-to-end test.
7. Conclude with three tests: real source, unknown fact, human approval. Share the [handout](https://scoopos-bowwow-masterclass.markgromer.workers.dev/?handout=1).

## Design
- 16 visual, editorial, 16:9 slide scenes, optimized for screen sharing.
- Interactive job-selection and safe-answer reveal, rather than a quiz that pretends to build an agent.
- Dedicated synchronized presenter window, slide pacing, elapsed timer, full screen, keyboard navigation, and an all-links resource hub.
- Printable student handout; no attendee data is collected.
- No proprietary assets, fonts, externally required JS frameworks, or student API keys in the deck. QR image requires the public QR service; the clickable lab link is always displayed.

## Architecture
`index.html` is the entire source. Deployed to a standalone Cloudflare Worker (not replacing the main Agent Lab).

The old beginner quiz is obsolete and redirects to the real Agent Lab. This deck is the lesson that precedes the Lab build.
