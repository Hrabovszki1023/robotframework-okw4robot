ExecuteJS JavaScript Snippets

Purpose: Quick one‑liners to use with the `ExecuteJS` keyword for web UIs.

Project‑specific (OKW4Robot demos)
- Get login status text (data-testid): `return document.querySelector('[data-testid="status-text"]')?.textContent?.trim();`
- Set username by test id: `document.querySelector('[data-testid="username"]').value='admin';`
- Set password by test id: `document.querySelector('[data-testid="password"]').value='secret';`
- Click login button: `document.querySelector('[data-testid="login"]').click();`
- Toggle checkbox (WidgetsDemo): `document.querySelector('[data-testid="cb-verheiratet"]').click();`
- Select combo item (WidgetsDemo):
  `const s=document.querySelector('[data-testid="combo-geschlecht"]'); if(s){ s.value='F'; s.dispatchEvent(new Event('change',{bubbles:true})); }`
- Pick radio by value within group name "zahlungsmethode":
  `document.querySelector('input[type=radio][name=zahlungsmethode][value=karte]')?.click();`
- Fill multiline note: `document.querySelector('[data-testid="ta-anmerkung"]').value='Hello\nWorld';`
- Scroll the page banner into view: `document.querySelector('[data-testid="widgets-demo-page"]').scrollIntoView({block:'center'});`

Read data
- Page title: `return document.title;`
- Element text: `return document.querySelector('#msg')?.textContent?.trim();`
- Input value: `return document.querySelector('#email')?.value ?? '';`
- Count elements: `return document.querySelectorAll('.item').length;`
- Read attribute: `return document.querySelector('#btn')?.getAttribute('data-id');`

Write/Interact
- Set input value: `document.querySelector('#email').value = 'user@example.com';`
- Click element: `document.querySelector('#submit')?.click();`
- Set attribute: `document.querySelector('#btn')?.setAttribute('aria-pressed','true');`
- Remove attribute: `document.querySelector('#btn')?.removeAttribute('disabled');`

Storage & cookies
- Set localStorage: `window.localStorage.setItem('flag','on');`
- Get localStorage: `return window.localStorage.getItem('flag');`
- Set cookie: `document.cookie = 'optin=yes; path=/;';`

Scrolling & viewport
- Scroll to element: `document.querySelector('#target')?.scrollIntoView({block:'center'});`
- Scroll to top: `window.scrollTo({top: 0, behavior: 'instant'});`

Regex/wildcard helpers
- Text matches regex: `return /hello\s+world/i.test(document.body.innerText);`
- Collect matching texts: `return [...document.querySelectorAll('li')].map(e=>e.textContent.trim()).filter(t=>/foo/.test(t));`

Network & events
- Dispatch event: `document.querySelector('#name')?.dispatchEvent(new Event('change', {bubbles:true}));`
- Trigger input: `const el=document.querySelector('#name'); if(el){ el.value='Max'; el.dispatchEvent(new Event('input',{bubbles:true})); }`

Notes
- Keep snippets idempotent and short; prefer `return ...` when you want a value back.
- These run in the page context and must obey the site's CSP and same‑origin policy.
- For anything used repeatedly, prefer adding/using a dedicated high‑level keyword.
