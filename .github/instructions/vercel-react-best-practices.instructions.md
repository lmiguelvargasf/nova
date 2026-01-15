---
applyTo: "frontend/**/*.{ts,tsx,js,jsx}"
---

# Vercel React Best Practices

Follow these performance-focused rules when writing or refactoring frontend
React/Next.js code in this repo.

For full examples and rationale, see `.github/skills/vercel-react-best-practices/rules/`.

## Eliminating waterfalls (critical)

- Start independent async work early; await late.
- Defer `await` into only the branches that use the result.
- Use `Promise.all()` for independent operations.
- For partial dependencies, use `better-all` style parallelization.
- For API routes/Server Actions, start auth/config/data in parallel.
- Prefer Suspense boundaries to stream slow sections.

## Bundle size optimization (critical)

- Avoid barrel imports; import from source paths.
- Use `next/dynamic` for heavy components.
- Defer non-critical third-party libs until after hydration.
- Conditionally load large modules when features are activated.
- Preload heavy bundles on user intent (hover/focus).

## Server-side performance (high)

- Use `React.cache()` for per-request deduplication.
- Use LRU caches for cross-request reuse (when appropriate).
- Minimize props crossing RSC boundaries; pass only needed fields.
- Compose Server Components to parallelize fetches.
- Use `after()` for non-blocking work.

## Client-side data fetching (medium-high)

- Use SWR for deduplication and caching.
- Deduplicate global event listeners across instances.

## Re-render optimization (medium)

- Read dynamic state at the point of use (avoid subscriptions).
- Memoize expensive subcomponents; enable early returns.
- Narrow effect dependencies to primitives/booleans.
- Use derived booleans to reduce re-render frequency.
- Use functional `setState` updates.
- Use lazy state initialization for expensive initial values.
- Use `startTransition` for non-urgent updates.

## Rendering performance (medium)

- Animate SVG wrappers, not SVG elements.
- Use React `Activity` for show/hide to preserve state/DOM in expensive toggles.
- Use `content-visibility: auto` for long lists.
- Hoist static JSX outside components.
- Reduce SVG precision where possible.
- Avoid hydration flicker via inline pre-hydration script for client-only data.
- Use explicit ternaries instead of `&&` when falsy values render.

## JavaScript performance (low-medium)

- Batch DOM style changes via classes or `cssText`.
- Build index maps for repeated lookups.
- Cache property access in hot loops.
- Cache repeated function results when inputs repeat.
- Cache storage reads; invalidate on external changes.
- Combine multiple array passes into one loop.
- Early return when possible.
- Check array lengths before expensive comparisons (sort, deep equality, serialization).
- Hoist RegExp creation or memoize it.
- Use loops for min/max instead of sorting.
- Use `Set`/`Map` for O(1) lookups.
- Use `toSorted()` instead of `sort()` to avoid mutation.

## Advanced patterns (low)

- Store event handlers in refs to prevent resubscriptions.
- Use a `useLatest` ref to avoid stale closures in effects.
