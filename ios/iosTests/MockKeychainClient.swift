import Foundation
import Security
@testable import ios

final class MockKeychainClient: KeychainClient, @unchecked Sendable {
    var storedData: Data?

    var copyStatus: OSStatus = errSecSuccess
    var addStatus: OSStatus = errSecSuccess
    var deleteStatus: OSStatus = errSecSuccess

    func copyMatching(_ query: CFDictionary) -> (OSStatus, CFTypeRef?) {
        switch copyStatus {
        case errSecSuccess:
            return (copyStatus, storedData as CFTypeRef?)
        case errSecItemNotFound:
            return (copyStatus, nil)
        default:
            return (copyStatus, nil)
        }
    }

    func add(_ query: CFDictionary) -> OSStatus {
        if addStatus == errSecSuccess {
            if let data = (query as NSDictionary)[kSecValueData as String] as? Data {
                storedData = data
            }
        }
        return addStatus
    }

    func delete(_ query: CFDictionary) -> OSStatus {
        if deleteStatus == errSecSuccess || deleteStatus == errSecItemNotFound {
            storedData = nil
        }
        return deleteStatus
    }
}
