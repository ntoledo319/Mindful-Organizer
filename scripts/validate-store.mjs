import { readFileSync, existsSync } from 'node:fs';
import { dirname, extname, isAbsolute, join, normalize, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const root = resolve(scriptDirectory, '..');
const failures = [];
let passed = 0;

function check(condition, message) {
  if (condition) {
    passed += 1;
  } else {
    failures.push(message);
  }
}

function pathInsideRoot(candidate) {
  const rel = relative(root, candidate);
  return rel === '' || (!rel.startsWith('..') && !isAbsolute(rel));
}

function workspacePath(relativePath) {
  const candidate = resolve(root, relativePath);
  check(pathInsideRoot(candidate), 'Path escapes workspace: ' + relativePath);
  return candidate;
}

function read(relativePath) {
  const candidate = workspacePath(relativePath);
  check(existsSync(candidate), 'Required file is missing: ' + relativePath);
  if (!existsSync(candidate)) return '';
  return readFileSync(candidate, 'utf8');
}

function parseJson(relativePath) {
  const source = read(relativePath);
  try {
    return JSON.parse(source);
  } catch (error) {
    failures.push('Invalid JSON in ' + relativePath + ': ' + error.message);
    return {};
  }
}

function isNonEmptyString(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

function isHttpsUrl(value) {
  if (!isNonEmptyString(value)) return false;
  try {
    return new URL(value).protocol === 'https:';
  } catch {
    return false;
  }
}

function checkStringLimit(value, limit, label) {
  check(isNonEmptyString(value), label + ' must be a non-empty string');
  if (typeof value === 'string') {
    check(value.length <= limit, label + ' is ' + value.length + '/' + limit + ' characters');
  }
}

const requiredFiles = [
  'README.md',
  'docs/PRIVACY.md',
  'docs/TERMS.md',
  'docs/REFUNDS.md',
  'docs/ACCESSIBILITY.md',
  'docs/SUPPORT.md',
  'docs/CAPABILITY_VAULT.md',
  'store/README.md',
  'store/SCREENSHOTS.md',
  'store/CAMPAIGNS.md',
  'store/PRODUCT-PAGE-EXPERIMENTS.md',
  'store/LAUNCH_KIT.md',
  'store/WINDOWS-VALIDATION.md',
  'store/POST_PUBLICATION_DOC_SWEEP.md',
  'store/identity.json',
  'store/listing-metadata.json',
  'landing/README.md',
  'landing/index.html',
  'landing/styles.css',
  'landing/robots.txt',
];

for (const file of requiredFiles) read(file);

const identity = parseJson('store/identity.json');
const listing = parseJson('store/listing-metadata.json');

check(listing.schemaVersion === 2, 'listing schemaVersion must be 2');
check(
  listing.releaseState === 'draft-not-publishable' || listing.releaseState === 'live',
  'listing releaseState must be draft-not-publishable or live',
);
checkStringLimit(listing.name, 50, 'name');
checkStringLimit(listing.shortDescription, 200, 'shortDescription');
checkStringLimit(listing.description, 10000, 'description');
checkStringLimit(listing.copyrightAndTrademarkInfo, 200, 'copyrightAndTrademarkInfo');
check(listing.language === 'en-us', 'first listing language must be en-us');

check(Array.isArray(listing.productFeatures), 'productFeatures must be an array');
if (Array.isArray(listing.productFeatures)) {
  check(
    listing.productFeatures.length > 0 && listing.productFeatures.length <= 20,
    'productFeatures must contain 1 to 20 entries',
  );
  for (const [index, feature] of listing.productFeatures.entries()) {
    checkStringLimit(feature, 200, 'productFeatures[' + index + ']');
  }
}

check(Array.isArray(listing.keywords), 'keywords must be an array');
if (Array.isArray(listing.keywords)) {
  check(listing.keywords.length > 0 && listing.keywords.length <= 7, 'keywords must contain 1 to 7 entries');
  const normalizedKeywords = listing.keywords.map((keyword) => String(keyword).trim().toLowerCase());
  check(new Set(normalizedKeywords).size === normalizedKeywords.length, 'keywords must be unique');
  for (const [index, keyword] of listing.keywords.entries()) {
    checkStringLimit(keyword, 40, 'keywords[' + index + ']');
  }
  const wordCount = listing.keywords
    .flatMap((keyword) => String(keyword).trim().split(/\s+/))
    .filter(Boolean).length;
  check(wordCount <= 21, 'keywords contain ' + wordCount + '/21 words');
}

check(listing.category?.primary === 'Productivity', 'primary category must be Productivity');
check(
  listing.category?.secondary === 'Health + fitness',
  'secondary category must be Health + fitness',
);
check(
  Array.isArray(listing.markets?.launch) && listing.markets.launch.includes('United States'),
  'launch markets must include United States',
);
check(isNonEmptyString(listing.ageRating?.status), 'ageRating.status is required');
check(Array.isArray(listing.ageRating?.contentToDisclose), 'ageRating.contentToDisclose is required');
check(Array.isArray(listing.accessibility?.verifiedInSource), 'accessibility.verifiedInSource is required');
check(Array.isArray(listing.accessibility?.blockedUntilVerified), 'accessibility.blockedUntilVerified is required');
check(listing.systemRequirements?.deviceFamily === 'Windows Desktop', 'device family must be Windows Desktop');
check(
  Array.isArray(listing.systemRequirements?.architecture) &&
    listing.systemRequirements.architecture.includes('x64'),
  'system requirements must include x64',
);
check(identity.productId === '9PLRSZZMFPJH', 'identity productId must match the reserved product');
check(
  typeof identity.identityVerified === 'boolean',
  'identityVerified must be a boolean backed by Partner Center observation',
);
if (identity.identityVerified !== true) {
  check(
    listing.releaseState === 'draft-not-publishable',
    'an unverified package identity requires draft-not-publishable release state',
  );
}
check(
  listing.urls?.storeListingPattern === 'https://apps.microsoft.com/detail/' + identity.productId,
  'Store listing pattern must match identity productId',
);

for (const key of ['privacyPolicy', 'terms', 'refundPolicy', 'source', 'support', 'plannedSupport', 'issueTracker', 'storeListingPattern']) {
  check(isHttpsUrl(listing.urls?.[key]), 'urls.' + key + ' must be an HTTPS URL');
}

if (listing.releaseState === 'draft-not-publishable') {
  check(listing.urls?.storeListing === null, 'draft Store URL must remain null until verified live');
} else {
  check(isHttpsUrl(listing.urls?.storeListing), 'live Store URL must be HTTPS');
}

for (const key of ['screenshotPlan', 'campaignPlan', 'experimentPlan', 'launchKit']) {
  const value = listing[key];
  check(isNonEmptyString(value), key + ' must name a local file');
  if (isNonEmptyString(value)) {
    const target = workspacePath(value);
    check(existsSync(target), key + ' target is missing: ' + value);
  }
}

const markdownFiles = requiredFiles.filter((file) => extname(file).toLowerCase() === '.md');
const markdownLinkPattern = /\[[^\]]+\]\((?!https?:|mailto:|#)([^)]+)\)/g;
for (const file of markdownFiles) {
  const source = read(file);
  for (const match of source.matchAll(markdownLinkPattern)) {
    const targetText = match[1].split('#')[0];
    if (!targetText) continue;
    const target = resolve(dirname(workspacePath(file)), targetText);
    check(pathInsideRoot(target), file + ' link escapes workspace: ' + targetText);
    check(existsSync(target), file + ' link target is missing: ' + targetText);
  }
}

const html = read('landing/index.html');
const css = read('landing/styles.css');
check(/<title>[^<]+<\/title>/.test(html), 'landing requires a document title');
check(/<meta\s+name="description"/.test(html), 'landing requires a meta description');
// JSON-LD structured-data blocks are the single permitted script form:
// inert <script type="application/ld+json"> with no src attribute. Carve-out
// added deliberately 2026-07-28 so deploy-time SEO structured data does not
// trip this invariant. Every other script — external or inline — stays
// forbidden, and a JSON-LD block carrying a src attribute fails below.
const ldJsonPattern = /<script\b[^>]*\btype\s*=\s*["']application\/ld\+json["'][^>]*>[\s\S]*?<\/script>/gi;
for (const block of html.match(ldJsonPattern) || []) {
  check(!/\bsrc\s*=/i.test(block), 'landing JSON-LD block must not load a src');
}
const htmlWithoutLdJson = html.replace(ldJsonPattern, '');
check(!/<script\b/i.test(htmlWithoutLdJson), 'landing must not load or embed scripts (inert application/ld+json excepted)');
check(!/<form\b/i.test(html), 'landing must not collect data through a form');
check(!/<iframe\b/i.test(html), 'landing must not embed iframes');
check(!/<img\b[^>]*\bsrc=["']https?:/i.test(html), 'landing must not load remote images');
check(
  !/<link\b[^>]*\brel=["']stylesheet["'][^>]*\bhref=["']https?:/i.test(html),
  'landing must not load a remote stylesheet',
);
check(!/@import\b/i.test(css), 'landing CSS must not import remote or local stylesheets');
check(!/url\(\s*["']?https?:/i.test(css), 'landing CSS must not load remote URL assets');
check(
  (css.match(/{/g) || []).length === (css.match(/}/g) || []).length,
  'landing CSS braces must be balanced',
);

const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);
check(new Set(ids).size === ids.length, 'landing HTML IDs must be unique');
for (const match of html.matchAll(/href="#([^"]+)"/g)) {
  check(ids.includes(match[1]), 'landing fragment target is missing: #' + match[1]);
}

for (const match of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
  const value = match[1];
  if (
    value.startsWith('#') ||
    value.startsWith('https://') ||
    value.startsWith('mailto:') ||
    value.startsWith('tel:') ||
    value.startsWith('sms:') ||
    value.startsWith('data:')
  ) {
    continue;
  }
  const withoutQuery = value.split(/[?#]/)[0];
  const target = resolve(root, 'landing', normalize(withoutQuery));
  check(pathInsideRoot(target), 'landing asset escapes workspace: ' + value);
  check(existsSync(target), 'landing local asset is missing: ' + value);
}

if (listing.releaseState === 'draft-not-publishable') {
  check(
    html.includes('data-release-state="prelaunch"'),
    'draft landing must expose data-release-state=prelaunch',
  );
  check(html.includes('Store release pending'), 'draft landing must say Store release pending');
  check(
    !html.includes('?cid=landing-primary'),
    'draft landing must not expose the live landing-primary purchase link',
  );
}

const campaigns = read('store/CAMPAIGNS.md');
check(campaigns.includes(identity.productId), 'campaign plan must use the reserved product ID');
check(campaigns.includes('landing-primary'), 'campaign plan must define landing-primary');

if (failures.length > 0) {
  console.error('Store validation failed with ' + failures.length + ' issue(s):');
  for (const failure of failures) console.error('- ' + failure);
  process.exitCode = 1;
} else {
  console.log('Store validation passed (' + passed + ' checks).');
}
