import Foundation
import Observation

@Observable
@MainActor
final class LoginViewModel {
    var email: String = ""
    var password: String = ""
    var isSubmitting = false
    var errorMessage: String?

    private let sessionStore: SessionStore

    init(sessionStore: SessionStore) {
        self.sessionStore = sessionStore
    }

    var canSubmit: Bool {
        let trimmedEmail = email.trimmingCharacters(in: .whitespacesAndNewlines)
        return !trimmedEmail.isEmpty && !password.isEmpty
    }

    func submit() async {
        guard canSubmit, !isSubmitting else {
            return
        }
        isSubmitting = true
        errorMessage = nil
        let trimmedEmail = email.trimmingCharacters(in: .whitespacesAndNewlines)
        do {
            try await sessionStore.login(email: trimmedEmail, password: password)
        } catch let apiError as APIError {
            errorMessage = apiError.userFacingMessage
        } catch {
            errorMessage = "Something went wrong. Please try again."
        }
        isSubmitting = false
    }
}
