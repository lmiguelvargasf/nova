import Foundation

final class InMemoryTokenStore: TokenStore {
    private var token: String?

    init(token: String? = nil) {
        self.token = token
    }

    func readToken() throws -> String? {
        token
    }

    func saveToken(_ token: String) throws {
        self.token = token
    }

    func clearToken() throws {
        token = nil
    }
}
