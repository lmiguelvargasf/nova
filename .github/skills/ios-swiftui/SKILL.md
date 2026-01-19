---
name: ios-swiftui
description: >
  Use when adding or modifying iOS Swift/SwiftUI code under ios/.
---

# iOS SwiftUI skill

## When to use

- You are working in `ios/` on Swift or SwiftUI files.
- You need to follow iOS 26+, Swift 6.2+, and modern SwiftUI guidance.
- You need MVVM structure with `@Observable` state models.

## Steps

1. Confirm new code targets iOS 26+ and Swift 6.2+.
2. Use `NavigationStack`, `navigationDestination(for:)`, and modern SwiftUI APIs.
3. Model shared state with `@Observable` + `@MainActor` classes.
4. Keep views as structs; move logic into view models for testability.
5. Avoid UIKit, `ObservableObject`, force unwraps, and legacy APIs.
6. Add unit tests for core logic.

## Constraints

- Do not add third-party frameworks without explicit approval.
- Avoid `onTapGesture()` unless tap location/count is required.
- Use `foregroundStyle()` and `clipShape(.rect(cornerRadius:))`.
- Use `Task.sleep(for:)` and `String.replacing(_:with:)`.
- Use `localizedStandardContains()` for user-input filtering.
