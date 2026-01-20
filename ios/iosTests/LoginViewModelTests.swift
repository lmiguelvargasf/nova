import XCTest
@testable import ios

final class LoginViewModelTests: XCTestCase {
    override func tearDown() {
        URLProtocolMock.requestHandler = nil
        super.tearDown()
    }

    @MainActor
    func testCanSubmitRequiresEmailAndPassword() async {
        let viewModel = LoginViewModel(sessionStore: makeSessionStore())

        viewModel.email = ""
        viewModel.password = ""
        XCTAssertFalse(viewModel.canSubmit)

        viewModel.email = "admin@local.dev"
        viewModel.password = ""
        XCTAssertFalse(viewModel.canSubmit)

        viewModel.email = ""
        viewModel.password = "password"
        XCTAssertFalse(viewModel.canSubmit)

        viewModel.email = "admin@local.dev"
        viewModel.password = "password"
        XCTAssertTrue(viewModel.canSubmit)
    }

    @MainActor
    func testCanSubmitTrimsEmail() async {
        let viewModel = LoginViewModel(sessionStore: makeSessionStore())
        viewModel.email = "   "
        viewModel.password = "password"
        XCTAssertFalse(viewModel.canSubmit)

        viewModel.email = " admin@local.dev "
        viewModel.password = "password"
        XCTAssertTrue(viewModel.canSubmit)
    }

    @MainActor
    func testSubmitSuccessUpdatesSessionAndClearsError() async {
        URLProtocolMock.requestHandler = { request in
            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 200,
                httpVersion: nil,
                headerFields: nil
            )!
            return (response, Self.loginResponseData)
        }
        let store = makeSessionStore()
        let viewModel = LoginViewModel(sessionStore: store)
        viewModel.email = "admin@local.dev"
        viewModel.password = "password"

        await viewModel.submit()

        XCTAssertNil(viewModel.errorMessage)
        XCTAssertFalse(viewModel.isSubmitting)
        switch store.status {
        case .authenticated(let user):
            XCTAssertEqual(user.email, "admin@local.dev")
        default:
            XCTFail("Expected authenticated status")
        }
    }

    @MainActor
    func testSubmitUnauthorizedSetsErrorMessage() async {
        URLProtocolMock.requestHandler = { request in
            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 401,
                httpVersion: nil,
                headerFields: nil
            )!
            return (response, Data())
        }
        let store = makeSessionStore()
        store.status = .unauthenticated
        let viewModel = LoginViewModel(sessionStore: store)
        viewModel.email = "admin@local.dev"
        viewModel.password = "wrong"

        await viewModel.submit()

        XCTAssertEqual(viewModel.errorMessage, APIError.unauthorized.userFacingMessage)
        XCTAssertFalse(viewModel.isSubmitting)
        switch store.status {
        case .unauthenticated:
            XCTAssertTrue(true)
        default:
            XCTFail("Expected unauthenticated status")
        }
    }

    @MainActor
    func testSubmitWhenInvalidDoesNotRun() async {
        let viewModel = LoginViewModel(sessionStore: makeSessionStore())
        viewModel.email = ""
        viewModel.password = ""

        await viewModel.submit()

        XCTAssertNil(viewModel.errorMessage)
        XCTAssertFalse(viewModel.isSubmitting)
    }

    @MainActor private func makeSessionStore() -> SessionStore {
        let config = URLSessionConfiguration.ephemeral
        config.protocolClasses = [URLProtocolMock.self]
        let session = URLSession(configuration: config)
        let client = APIClient(baseURL: URL(string: "http://localhost:8000")!, session: session)
        return SessionStore(apiClient: client, tokenStore: MockTokenStore())
    }

    private static let loginResponseData = Data(
        """
        {"token":"token","user":{"id":1,"email":"admin@local.dev","first_name":"M","last_name":"User"},"reactivated":false}
        """.utf8
    )
}
