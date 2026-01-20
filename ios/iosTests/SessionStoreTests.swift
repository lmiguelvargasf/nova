import XCTest
@testable import ios

final class SessionStoreTests: XCTestCase {
    func testRestoreSessionWithoutTokenSetsUnauthenticated() async {
        let tokenStore = MockTokenStore(token: nil)
        let store = SessionStore(apiClient: makeClient(), tokenStore: tokenStore)

        await store.restoreSession()

        switch store.status {
        case .unauthenticated:
            XCTAssertEqual(tokenStore.clearCallCount, 0)
        default:
            XCTFail("Expected unauthenticated status")
        }
    }

    func testRestoreSessionWithValidTokenLoadsUser() async {
        let tokenStore = MockTokenStore(token: "token")
        URLProtocolMock.requestHandler = { request in
            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 200,
                httpVersion: nil,
                headerFields: nil
            )!
            let data = Self.userResponseData
            return (response, data)
        }
        let store = SessionStore(apiClient: makeClient(), tokenStore: tokenStore)

        await store.restoreSession()

        switch store.status {
        case .authenticated(let user):
            XCTAssertEqual(user.email, "admin@local.dev")
        default:
            XCTFail("Expected authenticated status")
        }
    }

    func testRestoreSessionUnauthorizedClearsToken() async {
        let tokenStore = MockTokenStore(token: "token")
        URLProtocolMock.requestHandler = { request in
            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 401,
                httpVersion: nil,
                headerFields: nil
            )!
            return (response, Data())
        }
        let store = SessionStore(apiClient: makeClient(), tokenStore: tokenStore)

        await store.restoreSession()

        switch store.status {
        case .unauthenticated:
            XCTAssertEqual(tokenStore.clearCallCount, 1)
        default:
            XCTFail("Expected unauthenticated status")
        }
    }

    func testRestoreSessionServerErrorSetsErrorState() async {
        let tokenStore = MockTokenStore(token: "token")
        URLProtocolMock.requestHandler = { request in
            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 500,
                httpVersion: nil,
                headerFields: nil
            )!
            let data = Self.errorResponseData
            return (response, data)
        }
        let store = SessionStore(apiClient: makeClient(), tokenStore: tokenStore)

        await store.restoreSession()

        switch store.status {
        case .error:
            XCTAssertEqual(tokenStore.clearCallCount, 1)
        default:
            XCTFail("Expected error status")
        }
    }

    func testLoginSuccessStoresTokenAndUser() async throws {
        let tokenStore = MockTokenStore()
        URLProtocolMock.requestHandler = { request in
            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 200,
                httpVersion: nil,
                headerFields: nil
            )!
            let data = Self.loginResponseData
            return (response, data)
        }
        let store = SessionStore(apiClient: makeClient(), tokenStore: tokenStore)

        try await store.login(email: "admin@local.dev", password: "password")

        XCTAssertEqual(tokenStore.savedToken, "token")
        switch store.status {
        case .authenticated(let user):
            XCTAssertEqual(user.firstName, "M")
        default:
            XCTFail("Expected authenticated status")
        }
    }

    func testLoginUnauthorizedKeepsUnauthenticated() async {
        let tokenStore = MockTokenStore()
        URLProtocolMock.requestHandler = { request in
            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 401,
                httpVersion: nil,
                headerFields: nil
            )!
            return (response, Data())
        }
        let store = SessionStore(apiClient: makeClient(), tokenStore: tokenStore)
        store.status = .unauthenticated

        do {
            try await store.login(email: "admin@local.dev", password: "wrong")
            XCTFail("Expected login to throw")
        } catch {
            switch store.status {
            case .unauthenticated:
                XCTAssertEqual(tokenStore.savedToken, nil)
            default:
                XCTFail("Expected unauthenticated status")
            }
        }
    }

    func testLogoutClearsTokenAndResetsStatus() {
        let tokenStore = MockTokenStore(token: "token")
        let store = SessionStore(apiClient: makeClient(), tokenStore: tokenStore)
        store.status = .authenticated(User(id: 1, email: "admin@local.dev", firstName: "M", lastName: "User"))

        store.logout()

        switch store.status {
        case .unauthenticated:
            XCTAssertEqual(tokenStore.clearCallCount, 1)
        default:
            XCTFail("Expected unauthenticated status")
        }
    }

    private func makeClient() -> APIClient {
        let config = URLSessionConfiguration.ephemeral
        config.protocolClasses = [URLProtocolMock.self]
        let session = URLSession(configuration: config)
        return APIClient(baseURL: URL(string: "http://localhost:8000")!, session: session)
    }

    private static let userResponseData = Data(
        """
        {"id":1,"email":"admin@local.dev","first_name":"M","last_name":"User"}
        """.utf8
    )

    private static let loginResponseData = Data(
        """
        {"token":"token","user":{"id":1,"email":"admin@local.dev","first_name":"M","last_name":"User"},"reactivated":false}
        """.utf8
    )

    private static let errorResponseData = Data(
        """
        {"detail":"Server error"}
        """.utf8
    )
}
