import Foundation
import Security

protocol KeychainClient: Sendable {
    func copyMatching(_ query: CFDictionary) -> (OSStatus, CFTypeRef?)
    func add(_ query: CFDictionary) -> OSStatus
    func delete(_ query: CFDictionary) -> OSStatus
}

struct LiveKeychainClient: KeychainClient {
    func copyMatching(_ query: CFDictionary) -> (OSStatus, CFTypeRef?) {
        var item: CFTypeRef?
        let status = SecItemCopyMatching(query, &item)
        return (status, item)
    }

    func add(_ query: CFDictionary) -> OSStatus {
        SecItemAdd(query, nil)
    }

    func delete(_ query: CFDictionary) -> OSStatus {
        SecItemDelete(query)
    }
}
