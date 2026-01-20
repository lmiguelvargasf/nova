import Foundation
@testable import ios

final class MockTokenStore: TokenStore, @unchecked Sendable {
    private(set) var token: String?
    private(set) var savedToken: String?
    private(set) var clearCallCount = 0

    init(token: String? = nil) {
        self.token = token
    }

    func readToken() throws -> String? {
        token
    }

    func saveToken(_ token: String) throws {
        self.token = token
        savedToken = token
    }

    func clearToken() throws {
        token = nil
        clearCallCount += 1
    }
}
