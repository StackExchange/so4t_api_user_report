const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const html = fs.readFileSync(new URL('../index.html', `file://${__filename}`), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(script, 'inline script exists');

function loadPage() {
  const elements = new Map();
  const document = {
    getElementById(id) {
      if (!elements.has(id)) {
        elements.set(id, {
          textContent: '', className: '', hidden: false, disabled: false,
          children: [], addEventListener() {}, append(child) { this.children.push(child); },
          replaceChildren() { this.children = []; }
        });
      }
      return elements.get(id);
    },
    createElement() { return { textContent: '' }; }
  };
  const context = vm.createContext({ document, URL, Date, Number, Set, Map, Blob, console, setTimeout, clearTimeout, DOMException });
  vm.runInContext(script, context);
  return { context, document };
}

test('v3 URLs and UTC date boundaries', () => {
  const { context } = loadPage();
  assert.equal(vm.runInContext("apiBase('https://stackoverflowteams.com/c/my-team')", context),
    'https://api.stackoverflowteams.com/v3/teams/my-team');
  assert.equal(vm.runInContext("apiBase('https://example.stackenterprise.co')", context),
    'https://example.stackenterprise.co/api/v3');
  assert.throws(() => vm.runInContext("apiBase('http://example.com')", context), /HTTPS/);
  assert.throws(() => vm.runInContext("apiBase('https://stackoverflowteams.com/c/team?token=bad')", context), /query/);
  const dates = vm.runInContext("reportDates('2024-01-01', '2024-01-31')", context);
  assert.equal(dates.from, '2024-01-01T00:00:00.000Z');
  assert.equal(dates.to, '2024-02-01T00:00:00.000Z');
  assert.equal(vm.runInContext("inPeriod('2024-01-31T23:59:59Z', reportDates('2024-01-01','2024-01-31'))", context), true);
  assert.equal(vm.runInContext("inPeriod('2024-02-01T00:00:00Z', reportDates('2024-01-01','2024-01-31'))", context), false);
});

test('report uses v3 content, group SMEs, and Enterprise metadata', async () => {
  const { context } = loadPage();
  const calls = [];
  const data = {
    '/users': [{ id: 2, name: 'Ada, "A"', accountId: 12, reputation: 200, role: 'Moderator', email: 'ada@example.com', jobTitle: 'Engineer' },
      { id: 3, name: 'Bo', accountId: 13, reputation: 100, role: 'Member' }],
    '/users/manage': [{ id: 2, name: 'Ada', creationDate: '2020-01-01T00:00:00Z', lastAccessDate: '2024-01-31T00:00:00Z', isDeactivated: false },
      { id: 3, name: 'Bo', creationDate: '2020-01-01T00:00:00Z', lastAccessDate: '2023-01-01T00:00:00Z', isDeactivated: true }],
    '/users/reputation/aggregate': [{ userId: 2, reputationChange: 7 }],
    '/questions': [{ id: 10, owner: { id: 2 }, creationDate: '2023-01-01T00:00:00Z', answerCount: 1, score: 5 },
      { id: 11, owner: { id: 2 }, creationDate: '2024-01-05T00:00:00Z', answerCount: 0, score: -1 }],
    '/questions/10/answers': [{ id: 50, owner: { id: 3 }, questionId: 10, creationDate: '2024-01-10T00:00:00Z', isAccepted: true, score: 3 }],
    '/articles': [{ id: 20, owner: { id: 3 }, creationDate: '2024-01-20T00:00:00Z', score: 4 }],
    '/users/2/comments': [{ id: 30, creationDate: '2024-01-31T23:00:00Z' }, { id: 31, creationDate: '2024-02-01T00:00:00Z' }],
    '/users/3/comments': [],
    '/tags': [{ id: 8, name: 'javascript', subjectMatterExpertCount: 1 }]
  };
  const client = {
    async pages(path, params) { calls.push([path, params]); assert.ok(path in data, path); return data[path]; },
    async get(path) {
      assert.equal(path, '/tags/8/subject-matter-experts');
      return { users: [], userGroups: [{ id: 99, users: [{ id: 2 }] }] };
    }
  };
  context.client = client;
  const rows = await vm.runInContext("collectReport(client, { dates: reportDates('2024-01-01', '2024-01-31'), limit: null, includeComments: true, includeSmes: true, enterprise: true })", context);
  const ada = rows.find(row => row['User ID'] === 2);
  const bo = rows.find(row => row['User ID'] === 3);
  assert.equal(ada['Questions'], 1);
  assert.equal(ada['Questions With No Answers'], 1);
  assert.equal(ada['Question Score'], -1);
  assert.equal(ada['Comments'], 1);
  assert.equal(ada['SME Tags'], 'javascript');
  assert.equal(ada['Net Reputation Change'], 7);
  assert.equal(ada['Moderator'], true);
  assert.equal(bo['Answers'], 1);
  assert.equal(bo['Answers Accepted'], 1);
  assert.equal(bo['Answer Score'], 3);
  assert.equal(bo['Articles'], 1);
  assert.equal(bo['Account Status'], 'Deactivated');
  assert.ok(bo['Median Answer Time (Hours)'] > 0);
  assert.ok(calls.some(([path, params]) => path === '/users/reputation/aggregate' && params.from && params.to));
  context.rows = rows;
  const csv = vm.runInContext('toCsv(rows)', context);
  assert.match(csv, /"Ada, ""A"""/);
  assert.ok(csv.startsWith('\ufeff'));
  assert.ok(!csv.includes('Total Upvotes'));
  assert.equal(vm.runInContext("csvCell('=HYPERLINK(\"https://bad.example\")')", context),
    '"\'=HYPERLINK(""https://bad.example"")"');
  assert.equal(vm.runInContext('csvCell(-3)', context), '"-3"');
});

test('HTTP client uses bearer authentication and follows v3 pagination', async () => {
  const { context } = loadPage();
  const requests = [];
  context.fetch = async (url, options) => {
    requests.push({ url: String(url), options });
    const page = Number(url.searchParams.get('page'));
    return {
      ok: true,
      async json() { return { items: [{ id: page }], totalPages: 2 }; }
    };
  };
  context.signal = new AbortController().signal;
  const ids = await vm.runInContext("makeClient('https://example.stackenterprise.co/api/v3', 'secret-token', signal).pages('/users')", context);
  assert.equal(ids.length, 2);
  assert.equal(requests.length, 2);
  assert.match(requests[0].url, /\/api\/v3\/users\?page=1&pageSize=100$/);
  assert.equal(requests[0].options.headers.Authorization, 'Bearer secret-token');
  assert.ok(!requests[0].url.includes('secret-token'));
});

test('Basic/Business leaves unavailable columns blank', async () => {
  const { context, document } = loadPage();
  context.client = {
    async pages(path) {
      return { '/users': [{ id: 2, name: 'Ada', reputation: 10 }], '/questions': [], '/articles': [] }[path];
    }
  };
  const rows = await vm.runInContext("collectReport(client, { dates: reportDates('', ''), limit: null, includeComments: false, includeSmes: false, enterprise: false })", context);
  assert.equal(rows[0]['Net Reputation Change'], '');
  assert.equal(rows[0]['Account Longevity (Days)'], '');
  assert.equal(rows[0]['Comments'], '');
  assert.ok(document.getElementById('warnings').children.length > 0);
});

test('a user limit fetches only selected users’ answers', async () => {
  const { context } = loadPage();
  const calls = [];
  context.client = {
    async pages(path) {
      calls.push(path);
      return {
        '/users': [{ id: 2, name: 'Ada' }, { id: 3, name: 'Bo' }],
        '/questions': [{ id: 10, owner: { id: 3 }, creationDate: '2023-01-01T00:00:00Z', answerCount: 1 }],
        '/users/2/answers': [{ id: 50, questionId: 10, creationDate: '2024-01-10T00:00:00Z', score: 1 }],
        '/articles': []
      }[path];
    }
  };
  const rows = await vm.runInContext("collectReport(client, { dates: reportDates('2024-01-01', '2024-01-31'), limit: 1, includeComments: false, includeSmes: false, enterprise: false })", context);
  assert.equal(rows.length, 1);
  assert.equal(rows[0]['Answers'], 1);
  assert.ok(calls.includes('/users/2/answers'));
  assert.ok(!calls.includes('/questions/10/answers'));
  assert.ok(!calls.includes('/users/3/answers'));
});

test('missing Enterprise management permission leaves those fields blank', async () => {
  const { context, document } = loadPage();
  context.client = {
    async pages(path) {
      if (path === '/users/manage' || path === '/users/reputation/aggregate') throw new Error('API 403 at ' + path);
      return { '/users': [{ id: 2, name: 'Ada', reputation: 10 }], '/questions': [], '/articles': [] }[path];
    }
  };
  const rows = await vm.runInContext("collectReport(client, { dates: reportDates('', ''), limit: null, includeComments: false, includeSmes: false, enterprise: true })", context);
  assert.equal(rows[0]['Current Reputation'], 10);
  assert.equal(rows[0]['Net Reputation Change'], '');
  assert.equal(rows[0]['Account Status'], '');
  assert.equal(rows[0]['Account Longevity (Days)'], '');
  assert.ok(document.getElementById('warnings').children.length >= 2);
});
