# Practice Apps

Written by [Taki Sadik](../../about) · Last updated 2026-10-22 · 9 min read

TypeScript and web development practice projects, app_2_kimi, heda1, heda2

## Overview

This entry covers a collection of three practice web applications built while learning TypeScript and modern front-end development patterns. app_2_kimi is a TypeScript utility application that introduced the full TypeScript toolchain: npm project initialisation, tsconfig.json configuration, writing typed interfaces and functions, and compiling through tsc. heda1 is an HTML/CSS/JavaScript exercise focusing on interactive DOM manipulation and CSS layout practice with Flexbox. heda2 builds on heda1 with more advanced CSS Grid + Flexbox combined layouts and deeper JavaScript DOM patterns. Each project followed a consistent write → compile/lint → browser-test → refactor cycle, and the repositories document the progression from simple JavaScript patterns toward type-safe TypeScript development practices.

## Architecture

heda2 - Advanced Layout + JS

index.htmlMore Complex Structure

style.cssGrid + Flexbox Combined

app.jsAdvanced DOM PatternsDynamic Rendering

heda1 - JS Practice App

index.htmlSemantic Structure

style.cssFlexbox Layouts

app.jsDOM ManipulationEvent Listeners

app_2_kimi - TypeScript App

src/.ts source filesInterfaces · Types · Functions

tsconfig.jsonstrict mode · ES2020 target

tsc compileOutputs dist/*.js

BrowserLoads compiled JS

## Tech Stack

- TypeScript 5, Strict mode compiler, interfaces, type aliases, function parameter types, return type annotations

- tsc (TypeScript Compiler), tsconfig.json with strict: true, target: ES2020, outDir: dist, rootDir: src

- npm, Package management, package.json scripts for build and watch modes

- HTML5, Semantic markup for interactive UI elements in heda1 and heda2

- CSS3, Flexbox (heda1), CSS Grid combined with Flexbox (heda2)

- Vanilla JavaScript / TypeScript, DOM manipulation, event listeners, dynamic element creation and insertion

## Build Process

Initialised the project with npm init -y and installed TypeScript as a dev dependency. Generated a tsconfig.json using npx tsc --init and configured the key compiler options for a browser-targeted project with strict checking enabled.

// tsconfig.json (key settings)
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ES2020",
    "strict": true,
    "rootDir": "./src",
    "outDir": "./dist",
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}

// package.json scripts
"scripts": {
  "build": "tsc",
  "watch": "tsc --watch"
}

Defined TypeScript interfaces for the application's data structures. All function parameters and return types were explicitly annotated, forcing a design-first approach to function signatures and making the compiler catch shape mismatches at build time rather than at runtime.

// src/types.ts
interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user';
}

// src/utils.ts
function formatUser(user: User): string {
  return `${user.name} <${user.email}> [${user.role}]`;
}

function filterByRole(users: User[], role: User['role']): User[] {
  return users.filter(u => u.role === role);
}

Built a single-page practice app focusing on Flexbox layout patterns and JavaScript DOM manipulation. Interactive elements (buttons, inputs) were used as hooks to practice addEventListener, reading input values, creating new DOM elements with document.createElement, and inserting them with appendChild / insertBefore.

// heda1 - core pattern practiced
const addBtn = document.getElementById('add-item');
const listInput = document.getElementById('item-input');
const list = document.getElementById('item-list');

addBtn.addEventListener('click', () => {
  const text = listInput.value.trim();
  if (!text) return;
  const li = document.createElement('li');
  li.textContent = text;
  li.addEventListener('click', () => li.remove());
  list.appendChild(li);
  listInput.value = '';
});

Advanced the layout complexity by combining CSS Grid for macro page structure (header / sidebar / main / footer areas) with Flexbox for micro-component layout (nav items, card content). Practiced the pattern of using Grid for two-dimensional layout and Flexbox for one-dimensional alignment within Grid children.

/* heda2 - Grid macro layout */
.app-layout {
  display: grid;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
  grid-template-columns: 240px 1fr;
  grid-template-rows: auto 1fr auto;
  min-height: 100vh;
}

/* Flexbox within grid children */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
}

Each project used the same development loop: write TypeScript or JavaScript, run tsc --watch (or open the browser directly for plain JS), observe errors in the terminal or console, fix them, and refactor the code toward cleaner patterns. This cycle reinforced the habit of treating compiler errors and console warnings as primary feedback rather than treating them as noise to be dismissed.

Each project was managed in its own Git repository. Work was done on topic branches (feat/type-definitions, fix/strict-errors) with commit messages written to describe the intent of the change rather than the mechanical action ("Add User interface and filter utility" rather than "update types.ts"). This produced a commit history that reads as a learning narrative.

## TypeScript Development Cycle

Yes

No

Yes

No

Write .tsSource File

tsc --watchCompiler Running

Type Errors?

Compiler ReportsFile · Line · Error

Fix Type ErrorCorrect Interface / Type

dist/*.jsCompiled Output

Browser TestLoad HTML + dist/

Runtime Issues?

Debug in DevToolsConsole / Breakpoints

RefactorImprove Types / Structure

Git CommitMeaningful Message

## Challenges & Solutions

TypeScript Strict Mode Compiler Errors. Enabling "strict": true in tsconfig.json activates several sub-checks including strictNullChecks, noImplicitAny, and strictFunctionTypes. The initial codebase had several implicit any parameters and unchecked null returns from document.getElementById. The discipline required to satisfy the strict compiler, adding explicit types to every parameter, narrowing nullable DOM queries with type guards, was initially frustrating but produced significantly more robust code that caught real bugs at compile time.

Module Resolution with Older tsconfig Targets. Compiling ES6 module syntax (import/export) with an ES5-era configuration emitted CommonJS output (require/exports), which browsers cannot load natively, so the compiled app failed at runtime. The fix was to align the target and module settings, using ES2020 for both, and to serve the project via a local development server rather than opening the compiled HTML as a file:// URL, which does not support ES modules due to CORS restrictions.

## What I Learned

- Setting up a TypeScript project from scratch: npm init, tsc --init, configuring tsconfig.json rootDir, outDir, target, and module options

- TypeScript interfaces define the shape of objects and create a compile-time contract between the data model and the code that uses it

- strict: true is the correct default for new TypeScript projects, the additional friction of satisfying the compiler pays dividends in caught bugs

- document.getElementById returns HTMLElement | null, null checks or non-null assertions are required in strict TypeScript before accessing element properties

- CSS Grid is best used for two-dimensional page-level layouts; Flexbox is best used for one-dimensional component-level alignment; combining both at different levels of the DOM is the standard production pattern

- Meaningful commit messages that describe intent (not mechanism) produce a version history that is genuinely useful for understanding how a project evolved

## How I Built It

Phase 1: Toolchain setup for app_2_kimi. The first project was deliberately a toolchain exercise: npm init, tsc --init, then configuring rootDir, outDir, target, and module in tsconfig.json before writing any real code. Typed interfaces and functions came next, compiled through tsc with "strict": true from the start.

Phase 2: Strict mode discipline. Satisfying strictNullChecks and noImplicitAny meant adding explicit types to every parameter and narrowing nullable DOM queries (like document.getElementById returning HTMLElement | null) with type guards. The compiler caught real bugs in exchange for the extra friction.

Phase 3: heda1, DOM manipulation fundamentals. The second project focused on interactive DOM manipulation and CSS Flexbox layouts in plain JavaScript, practicing the patterns that TypeScript would later type-check.

Phase 4: heda2, combined layouts. The third project layered CSS Grid for page-level structure over Flexbox for component-level alignment, with deeper JavaScript DOM patterns. Grid and Flexbox at different levels of the DOM is the standard production pattern this exercise was designed to teach.

Phase 5: The refactor loop. Every project followed a consistent cycle: write, compile or lint, test in the browser, then refactor. The repositories document the progression from simple JavaScript patterns toward type-safe TypeScript, and meaningful commit messages (intent over mechanism) make that history readable.

## What You Need

| Category | Item | Notes |
| --- | --- | --- |
| Tool | Node.js and npm | Project initialisation and the TypeScript compiler |
| Tool | TypeScript (tsc) | Compiles the typed source to browser-ready JavaScript |
| Tool | A local dev server | Required for ES module syntax: file:// URLs do not support ES modules due to CORS |
| Software | Code editor with TypeScript support | Inline type errors while writing, not just at compile time |
| Software | A modern web browser | DevTools console for testing compiled output |
| Skill | JavaScript fundamentals | The language TypeScript compiles to; learn it first |
| Skill | TypeScript type system | Interfaces, strict mode, nullable narrowing, aligned target/module config |
| Skill | CSS Grid and Flexbox | Grid for page structure, Flexbox for component alignment |

## Challenges and Lessons Learned

Strict mode frustration is a feature. The strict compiler rejected implicit any parameters and unchecked nulls at first, and working through those errors was slow. But the discipline produced code that caught real bugs at compile time instead of at runtime. Lesson: "strict": true is the correct default for every new TypeScript project, and the friction is the price of the safety.

Target and module must agree. Compiling ES6 module syntax down to an ES5 target broke module resolution in the browser, and opening the result over file:// added a second CORS failure. Aligning target and module (ES2020 for both) and serving over HTTP fixed both. Lesson: the tsconfig options are a system, not independent knobs.

Write the history you want to read. Commit messages describing intent rather than mechanism turned three small practice repos into a readable story of skill progression. That habit costs nothing and pays off every time you revisit a project.

## What Is Next

- A fourth project with a real framework (e.g. a TypeScript React app) to apply the fundamentals at production scale

- Unit testing with a framework like Vitest or Jest for the utility functions in app_2_kimi

- ESLint and Prettier integration for consistent linting alongside the strict compiler

- A shared TypeScript project template (tsconfig, lint config, dev server) so future projects start correctly configured

- Publishing a small typed utility package to npm as a packaging exercise

## Related Projects

- Birthday Project, an interactive celebration page.

- Pharmacy Website, a medical and pharmacy site.

- Faiaz Shisha, a multi-page business site with booking.
