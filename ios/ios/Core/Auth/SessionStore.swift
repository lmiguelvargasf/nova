import Foundation
import Observation

@Observable
@MainActor
final class SessionStore {
    var status: SessionStatus = .checking

    private let apiClient: APIClient
    private let tokenStore: TokenStore

    init(apiClient: APIClient = .live(), tokenStore: TokenStore = KeychainTokenStore()) {
        self.apiClient = apiClient
        self.tokenStore = tokenStore
    }

    func restoreSession() async {
        status = .checking
        do {
            let token = try tokenStore.readToken()
            guard let token else {
                status = .unauthenticated
                return
            }
            let user = try await apiClient.getCurrentUser(token: token)
            status = .authenticated(user)
        } catch APIError.unauthorized {
            try? tokenStore.clearToken()
            status = .unauthenticated
        } catch {
            try? tokenStore.clearToken()
            status = .error("We couldn’t restore your session. Please try again.")
        }
    }

    func login(email: String, password: String) async throws {
        let response = try await apiClient.login(email: email, password: password)
        try tokenStore.saveToken(response.token)
        status = .authenticated(response.user)
    }

    func logout() {
        try? tokenStore.clearToken()
        status = .unauthenticated
    }
}
