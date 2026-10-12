import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import test from 'node:test';

const path = process.env.BLUEPRINT_HTML || new URL('../index.html', import.meta.url);
const html = readFileSync(path, 'utf8');
const start = html.includes('const BLUEPRINT_MAX_BYTES=') ? html.indexOf('const BLUEPRINT_MAX_BYTES=') : html.indexOf('function exportBlueprint(){');
const end = html.indexOf('function download(', start);
const implementation = html.slice(start, end);
const base = () => ({ mission: 'leads', name: 'Demo Agent', business: 'Fictional Workshop', services: 'Pet cleanup', area: 'UNKNOWN', policies: 'UNKNOWN', knowledge: 'fictional.csv', trigger: 'On request', workflow: 'Read, draft, approve', done: 'Cite a source', source: 'Airtable', escalation: 'Unknown facts', mode: 'project', tools: ['Airtable'], checks: [true, true, true], testEvidence: 'TEST-ID', step: 5 });
function harness(initial = base()) {
 const result = { downloads: [], feedback: [], saves: 0, renders: 0 };
 const missionNodes = ['leads', 'inbox', 'daily', 'service'].map(mission => { const node = { dataset: { mission }, selected: mission === initial.mission }; node.classList = { toggle(name, selected) { if (name === 'selected') node.selected = selected; } }; return node; });
 const context = vm.createContext({ st: structuredClone(initial), defaults: { leads: {}, inbox: {}, daily: {}, service: {} }, toolList: ['Airtable', 'Gmail', 'Google Calendar', 'Google Drive'], Blob, Date,
  collect() {}, download(name, content, mime) { result.downloads.push({ name, content, mime }); },
  feedback(id, message, kind) { result.feedback.push({ id, message, kind }); },
  document: { querySelectorAll() { return missionNodes; } }, render() { result.renders++; }, show(step) { context.st.step = step; }, save() { result.saves++; }
 });
 vm.runInContext(implementation, context);
 return { context, result, selectedMissions: () => missionNodes.filter(node => node.selected).map(node => node.dataset.mission), state: () => JSON.parse(JSON.stringify(context.st)), export: () => context.exportBlueprint(), import: content => context.importBlueprint({ size: new Blob([content]).size, text: async () => content }) };
}
const envelope = state => JSON.stringify({ app: 'scoopos-agent-lab', schema: 1, state });

test('long business knowledge, policy and workflow text round-trips without truncation', async () => {
 const initial = base();
 for (const key of ['policies', 'knowledge', 'workflow']) initial[key] = `${key}:` + 'a'.repeat(4096) + ' END';
 const h = harness(initial); h.export();
 assert.equal(h.result.downloads.length, 1);
 const exported = h.result.downloads[0].content;
 h.context.st = base();
 await h.import(exported);
 for (const key of ['policies', 'knowledge', 'workflow']) assert.equal(h.state()[key], initial[key]);
 assert.deepEqual(h.state().checks, [false, false, false]);
 assert.equal(h.state().testEvidence, '');
 assert.equal(h.state().step, 1);
});

test('Unicode text over 2500 characters remains exact', async () => {
 const initial = base(); initial.knowledge = '🐶 你好 café\n'.repeat(500);
 const h = harness(initial); h.export(); await h.import(h.result.downloads[0].content);
 assert.equal(h.state().knowledge, initial.knowledge);
});

test('export rejects oversized backup without downloading or changing configuration', () => {
 const initial = base(); initial.knowledge = 'x'.repeat(65536);
 const h = harness(initial); h.export();
 assert.equal(h.result.downloads.length, 0);
 assert.match(h.result.feedback.at(-1)?.message || '', /64 KB/);
 assert.deepEqual(h.state(), initial);
});

test('export limit measures UTF-8 bytes rather than character count', () => {
 const initial = base(); initial.knowledge = '🐶'.repeat(17000);
 const h = harness(initial); h.export();
 assert.equal(h.result.downloads.length, 0);
 assert.match(h.result.feedback.at(-1)?.message || '', /64 KB/);
});

test('exactly 64 KiB export is accepted and can be imported; one more byte is rejected', async () => {
 const h = harness(); h.export();
 const overhead = new Blob([h.result.downloads[0].content]).size;
 const size = 65536 - overhead + base().knowledge.length;
 h.context.st.knowledge = 'x'.repeat(size); h.result.downloads.length = 0; h.export();
 assert.equal(h.result.downloads.length, 1);
 assert.equal(new Blob([h.result.downloads[0].content]).size, 65536);
 await h.import(h.result.downloads[0].content);
 assert.equal(h.state().knowledge.length, size);
 h.context.st.knowledge += 'x'; h.result.downloads.length = 0; h.export();
 assert.equal(h.result.downloads.length, 0);
});

test('oversized import fails before read and leaves prior configuration unchanged', async () => {
 const h = harness(); let read = false;
 await h.context.importBlueprint({ size: 65537, text: async () => { read = true; return envelope(base()); } });
 assert.equal(read, false); assert.deepEqual(h.state(), base());
 assert.equal(h.result.saves, 0); assert.match(h.result.feedback.at(-1)?.message || '', /unchanged/);
});

test('malformed JSON and unsupported schema leave prior configuration unchanged', async () => {
 for (const content of ['{bad', 'null', JSON.stringify({ app: 'scoopos-agent-lab', schema: 2, state: base() })]) {
  const h = harness(); await h.import(content);
  assert.deepEqual(h.state(), base()); assert.equal(h.result.saves, 0);
  assert.match(h.result.feedback.at(-1)?.message || '', /unchanged/);
 }
});

test('unknown and prototype-property mission names are rejected without mutation', async () => {
 for (const mission of ['unknown', '__proto__', 'constructor', 'toString']) {
  const h = harness(); await h.import(envelope({ ...base(), mission, business: 'MUST NOT APPLY' }));
  assert.deepEqual(h.state(), base()); assert.equal(h.result.saves, 0);
 }
});

test('cancelling file selection leaves configuration and feedback unchanged', async () => {
 const h = harness(); await h.context.importBlueprint(undefined);
 assert.deepEqual(h.state(), base()); assert.equal(h.result.feedback.length, 0); assert.equal(h.result.saves, 0);
});


test('an interrupted render rolls back configuration, stage and persisted state', async () => {
 const h = harness(); let attempts = 0; let saved = null;
 h.context.render = () => { if (++attempts === 1) throw new Error('interrupted render'); };
 h.context.save = () => { saved = h.state(); };
 await h.import(envelope({ ...base(), mission: 'inbox', business: 'REPLACEMENT', knowledge: 'different facts' }));
 assert.deepEqual(h.state(), base());
 assert.deepEqual(saved, base());
 assert.equal(attempts, 2);
 assert.deepEqual(h.selectedMissions(), ['leads']);
 assert.match(h.result.feedback.at(-1)?.message || '', /unchanged/);
});
