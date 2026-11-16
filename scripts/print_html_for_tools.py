import os
import json

#CE: Tools tab. Jumpstart sources are JSON files in resources/jumpstart, one per product:
#CE: { "code": "J22", "name": "...", "packs": [ { "name", "theme", "header", "cards": [[qty, name, number], ...] } ] }

PAGE_JS = '''
	document.getElementById("search").addEventListener("keypress", function(event) {
		if (event.key === "Enter") {
			event.preventDefault();
			const url = new URL(rootPath + '/search', window.location.href.split('?')[0].split('/').slice(0, -1).join('/') + '/');
			url.searchParams.append('search', document.getElementById("search").value);
			window.location.href = url.pathname + url.search;
		}
	});

	function randomCard() {
		fetch(rootPath + '/lists/all-cards.json')
			.then(response => response.json())
			.then(data => {
				const card = data.cards[Math.floor(Math.random() * data.cards.length)];
				const url = new URL(rootPath + '/card', window.location.href.split('?')[0].split('/').slice(0, -1).join('/') + '/');
				url.searchParams.append('set', card.set);
				url.searchParams.append('num', card.number);
				url.searchParams.append('name', card.card_name);
				window.location.href = url.pathname + url.search;
			}).catch(error => console.error('Error:', error));
	}
'''

STYLE = '''
	@font-face {
		font-family: Beleren;
		src: url('./resources/beleren.ttf');
	}
	@font-face {
		font-family: 'Gotham Narrow Medium';
		src: url('./resources/gotham-narrow-medium.otf');
	}
	body {
		font-family: 'Open Sans', 'Helvetica', 'Arial', sans-serif;
		overscroll-behavior: none;
		margin: 0px;
		background-color: #f3f3f3;
	}
	.tools-container {
		width: 80%;
		max-width: 900px;
		margin: 40px auto;
	}
	h1 {
		font-family: Beleren;
		font-size: 32px;
		font-weight: normal;
		margin: 0 0 20px 0;
		border-bottom: 2px solid #171717;
		padding-bottom: 10px;
	}
	.panel {
		background-color: white;
		border: 1px solid #d5d9d9;
		border-radius: 8px;
		padding: 20px;
		margin-bottom: 20px;
	}
	a.tool-link {
		display: block;
		color: inherit;
		text-decoration: none;
	}
	a.tool-link:hover .tool-title {
		text-decoration: underline;
	}
	.tool-title {
		font-family: 'Gotham Narrow Medium', sans-serif;
		font-size: 20px;
	}
	.tool-desc {
		color: #666;
		font-size: 14px;
	}
	button {
		font-family: inherit;
		font-size: 14px;
		background-color: #171717;
		color: #f3f3f3;
		border: none;
		border-radius: 2px;
		padding: 8px 16px;
		cursor: pointer;
	}
	button:hover {
		background-color: #333333;
	}
	label {
		display: block;
		margin-bottom: 8px;
	}
	.headers {
		display: flex;
		gap: 20px;
		justify-content: center;
		flex-wrap: wrap;
	}
	.headers figure {
		margin: 0;
		text-align: center;
	}
	.headers img {
		width: 250px;
		border-radius: 12px;
		display: block;
	}
	.headers figcaption {
		margin-top: 8px;
		font-family: 'Gotham Narrow Medium', sans-serif;
	}
	.list-bar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 10px;
	}
	pre {
		margin: 0;
		font-family: inherit;
		font-size: 15px;
		line-height: 1.5;
		white-space: pre-wrap;
	}
'''

def page(title, icon, body, script=''):
	header_snippet = ''
	with open(os.path.join('scripts', 'snippets', 'header.txt'), encoding='utf-8-sig') as f:
		header_snippet = f.read()
	return f'''<html>
<head>
	<title>{title}</title>
	<link rel="icon" type="image/x-icon" href="./img/{icon}">
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300..800;1,300..800&display=swap" rel="stylesheet">
	<link rel="stylesheet" href="./resources/header.css">
</head>
<script title="root">
	const rootPath = ".";
</script>
<style>{STYLE}</style>
<body>
	{header_snippet}
	<div class="tools-container">
{body}
	</div>
	<script>{PAGE_JS}{script}</script>
</body>
</html>'''

def generateJumpstart():
	js_dir = os.path.join('resources', 'jumpstart')
	sources = []
	if os.path.isdir(js_dir):
		for entry in sorted(os.scandir(js_dir), key=lambda e: e.name):
			if entry.name.endswith('.json'):
				with open(entry.path, encoding='utf-8-sig') as f:
					data = json.load(f)
				sources.append({ 'file': entry.name, 'code': data['code'], 'name': data['name'], 'count': len(data['packs']) })

	checkboxes = '\n'.join(
		f'\t\t\t<label><input type="checkbox" class="js-source" value="{s["file"]}" checked> {s["name"]} ({s["code"]}, {s["count"]} packs)</label>'
		for s in sources
	)

	body = f'''		<h1>Jumpstart</h1>
		<div class="panel">
{checkboxes}
			<button onclick="generate()">Generate deck</button>
		</div>
		<div id="result" style="display: none;">
			<div class="panel headers" id="headers"></div>
			<div class="panel">
				<div class="list-bar">
					<span class="tool-title">Decklist</span>
					<button id="copy-btn" onclick="copyList()">Copy</button>
				</div>
				<pre id="decklist"></pre>
			</div>
		</div>'''

	script = '''
	const BASICS = [ 'Plains', 'Island', 'Swamp', 'Mountain', 'Forest', 'Wastes' ];
	const loaded = {};

	async function loadSource(file) {
		if (!loaded[file]) {
			const data = await fetch(rootPath + '/resources/jumpstart/' + file).then(r => r.json());
			data.packs.forEach(p => p.code = data.code);
			loaded[file] = data;
		}
		return loaded[file];
	}

	async function generate() {
		const files = [...document.querySelectorAll('.js-source:checked')].map(c => c.value);
		const pool = (await Promise.all(files.map(loadSource))).flatMap(d => d.packs);
		if (pool.length == 0) return;

		// Normal Jumpstart: open two random boosters and shuffle them together.
		const packs = [ pool[Math.floor(Math.random() * pool.length)], pool[Math.floor(Math.random() * pool.length)] ];

		const merged = new Map();
		for (const pack of packs) {
			for (const [qty, name, num] of pack.cards) {
				const key = name + '|' + pack.code + '|' + num;
				if (merged.has(key)) merged.get(key).qty += qty;
				else merged.set(key, { qty, name, code: pack.code, num });
			}
		}
		const lines = [...merged.values()]
			.sort((a, b) => BASICS.includes(a.name) - BASICS.includes(b.name))
			.map(c => `${c.qty} ${c.name} (${c.code})${c.num ? ' ' + c.num : ''}`);

		const headers = document.getElementById('headers');
		headers.innerHTML = '';
		for (const pack of packs) {
			const fig = document.createElement('figure');
			if (pack.header) {
				const img = document.createElement('img');
				img.src = pack.header;
				img.alt = pack.theme;
				fig.appendChild(img);
			}
			const cap = document.createElement('figcaption');
			cap.textContent = pack.name;
			fig.appendChild(cap);
			headers.appendChild(fig);
		}
		document.getElementById('decklist').textContent = lines.join('\\n');
		document.getElementById('copy-btn').textContent = 'Copy';
		document.getElementById('result').style.display = 'block';
	}

	function copyList() {
		navigator.clipboard.writeText(document.getElementById('decklist').textContent)
			.then(() => document.getElementById('copy-btn').textContent = 'Copied!');
	}
'''
	with open('jumpstart.html', 'w', encoding='utf-8') as f:
		f.write(page('Jumpstart', 'tools.png', body, script))
	print('Generated jumpstart.html')

def generateHTML():
	generateJumpstart()

	body = '''		<h1>Tools</h1>
		<div class="panel">
			<a class="tool-link" href="./jumpstart">
				<div class="tool-title">Jumpstart</div>
				<div class="tool-desc">Open two random Jumpstart boosters and get the combined decklist.</div>
			</a>
		</div>'''
	with open('all-tools.html', 'w', encoding='utf-8') as f:
		f.write(page('Tools', 'tools.png', body))
	print('Generated all-tools.html')

if __name__ == '__main__':
	generateHTML()
