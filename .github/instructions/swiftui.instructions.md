---
applyTo: "ios/**/*.swift"
---

# Swift + SwiftUI instructions

## Scope and platform targets

- Target iOS 26.0+ and Swift 6.2+.
- Use SwiftUI as the primary UI framework; avoid UIKit unless explicitly
  requested.
- Do not add third-party dependencies without explicit approval.

## Architecture and structure

- Follow MVVM with shared state in `@Observable` models.
- Always mark `@Observable` classes with `@MainActor`.
- Prefer value types for views and data models; use classes only for shared
  state or reference semantics.
- Keep one primary type per file; split new types into new files.
- Organize files by feature under `ios/` (e.g., `Features/`, `Core/`, `UI/`,
  `Resources/`).

## Swift language and concurrency

- Assume strict Swift concurrency; use `async`/`await`.
- Never use `DispatchQueue.main.async()`; use modern Swift concurrency.
- Never use `Task.sleep(nanoseconds:)`; use `Task.sleep(for:)`.
- Avoid force unwraps and force `try` unless unrecoverable; prefer safe handling.
- Prefer Swift-native APIs over Foundation legacy variants:
  - `String.replacing(_:with:)` over `replacingOccurrences(of:with:)`.
  - `URL.documentsDirectory` and `appending(path:)` for file URLs.

## SwiftUI standards

- Always use `NavigationStack` and `navigationDestination(for:)`.
- Always use `foregroundStyle()` instead of `foregroundColor()`.
- Always use `clipShape(.rect(cornerRadius:))` instead of `cornerRadius()`.
- Always use the `Tab` API instead of `tabItem()`.
- Never use `ObservableObject` or `@Published`; prefer `@Observable`.
- Never use `onChange()` 1-parameter variant; use 0- or 2-parameter variants.
- Avoid `onTapGesture()`; use `Button` unless tap location/Count is required.
- Avoid `AnyView` unless strictly necessary.
- Avoid hard-coded font sizes and fixed padding/spacing unless requested;
  support Dynamic Type.
- Use `.scrollIndicators(.hidden)` to hide scroll indicators.
- Do not use `UIScreen.main.bounds` or `GeometryReader` if newer alternatives
  work.
- If a `Button` label uses an image, include text:
  `Button("Title", systemImage: "plus", action: ...)`.
- Use `ImageRenderer` instead of `UIGraphicsImageRenderer` for SwiftUI
  rendering.
- Use `bold()` instead of `fontWeight(.bold)` unless there is a strong
  reason.
- When filtering user-input text, use `localizedStandardContains()`.

## SwiftUI view composition

- Do not split views into computed properties; extract subviews into new
  `View` structs.
- Put view logic into view models for testability.
- When using `ForEach` with `enumerated()`, do not convert to an array.

## Data and storage

- If SwiftData uses CloudKit:
  - Never use `@Attribute(.unique)`.
  - Properties must have defaults or be optional.
  - All relationships must be optional.
- Use appropriate storage: UserDefaults for preferences, Keychain for sensitive
  data.

## Testing and quality

- Add unit tests for core logic; use UI tests only if unit tests are not
  possible.
- Keep code readable and concise; avoid placeholders or TODOs.
- If SwiftLint is installed, ensure it passes before declaring work complete.

## Accessibility and HIG

- Follow Apple Human Interface Guidelines.
- Support dynamic type, dark mode, and accessibility where applicable.
