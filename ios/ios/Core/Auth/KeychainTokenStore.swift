import Foundation
import Security

struct KeychainTokenStore: TokenStore, Sendable {
    enum StoreError: Error {
        case unexpectedStatus(OSStatus)
    }

    private let service: String
    private let account: String
    private let client: KeychainClient

    init(
        service: String = Bundle.main.bundleIdentifier ?? "NovaApp",
        account: String = "authToken",
        client: KeychainClient = LiveKeychainClient()
    ) {
        self.service = service
        self.account = account
        self.client = client
    }

    func readToken() throws -> String? {
        var query = baseQuery
        query[kSecMatchLimit as String] = kSecMatchLimitOne
        query[kSecReturnData as String] = true

        let (status, item) = client.copyMatching(query as CFDictionary)
        if status == errSecItemNotFound {
            return nil
        }
        guard status == errSecSuccess else {
            throw StoreError.unexpectedStatus(status)
        }
        guard let data = item as? Data else {
            return nil
        }
        return String(data: data, encoding: .utf8)
    }

    func saveToken(_ token: String) throws {
        _ = client.delete(baseQuery as CFDictionary)
        var query = baseQuery
        query[kSecValueData as String] = Data(token.utf8)

        let status = client.add(query as CFDictionary)
        guard status == errSecSuccess else {
            throw StoreError.unexpectedStatus(status)
        }
    }

    func clearToken() throws {
        let status = client.delete(baseQuery as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw StoreError.unexpectedStatus(status)
        }
    }

    private var baseQuery: [String: Any] {
        [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
    }
}
