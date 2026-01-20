import Security
import XCTest
@testable import ios

@MainActor final class KeychainTokenStoreTests: XCTestCase {
    func testSaveReadAndClearToken() throws {
        let client = MockKeychainClient()
        let store = KeychainTokenStore(client: client)

        try store.saveToken("token")
        let readToken = try store.readToken()
        XCTAssertEqual(readToken, "token")

        try store.clearToken()
        let clearedToken = try store.readToken()
        XCTAssertNil(clearedToken)
    }

    func testReadTokenReturnsNilWhenNotFound() throws {
        let client = MockKeychainClient()
        client.copyStatus = errSecItemNotFound
        let store = KeychainTokenStore(client: client)

        let token = try store.readToken()
        XCTAssertNil(token)
    }

    func testSaveTokenThrowsOnFailure() {
        let client = MockKeychainClient()
        client.addStatus = errSecIO
        let store = KeychainTokenStore(client: client)

        XCTAssertThrowsError(try store.saveToken("token")) { error in
            guard case KeychainTokenStore.StoreError.unexpectedStatus(let status) = error else {
                return XCTFail("Expected StoreError")
            }
            XCTAssertEqual(status, errSecIO)
        }
    }

    func testReadTokenThrowsOnFailure() {
        let client = MockKeychainClient()
        client.copyStatus = errSecAuthFailed
        let store = KeychainTokenStore(client: client)

        XCTAssertThrowsError(try store.readToken()) { error in
            guard case KeychainTokenStore.StoreError.unexpectedStatus(let status) = error else {
                return XCTFail("Expected StoreError")
            }
            XCTAssertEqual(status, errSecAuthFailed)
        }
    }

    func testClearTokenThrowsOnFailure() {
        let client = MockKeychainClient()
        client.deleteStatus = errSecInteractionNotAllowed
        let store = KeychainTokenStore(client: client)

        XCTAssertThrowsError(try store.clearToken()) { error in
            guard case KeychainTokenStore.StoreError.unexpectedStatus(let status) = error else {
                return XCTFail("Expected StoreError")
            }
            XCTAssertEqual(status, errSecInteractionNotAllowed)
        }
    }
}
