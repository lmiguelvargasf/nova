import XCTest
@testable import ios

final class APIClientTests: XCTestCase {
    override func tearDown() {
        URLProtocolMock.requestHandler = nil
        super.tearDown()
    }

    func testLoginBuildsRequestAndParsesResponse() async throws {
        URLProtocolMock.requestHandler = { request in
            XCTAssertEqual(request.httpMethod, "POST")
            XCTAssertEqual(request.value(forHTTPHeaderField: "Accept"), "application/json")
            XCTAssertEqual(request.value(forHTTPHeaderField: "Content-Type"), "application/json")
            XCTAssertEqual(request.url?.path, "/api/auth/login")

            let body = try XCTUnwrap(request.httpBody)
            let payload = String(decoding: body, as: UTF8.self)
            XCTAssertTrue(payload.contains("\"email\""))
            XCTAssertTrue(payload.contains("\"password\""))

            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 200,
                httpVersion: nil,
                headerFields: nil
            )!
            return (response, Self.loginResponseData)
        }

        let client = makeClient()
        let response = try await client.login(email: "admin@local.dev", password: "password")

        XCTAssertEqual(response.token, "token")
        XCTAssertEqual(response.user.email, "admin@local.dev")
    }

    func testGetCurrentUserBuildsAuthorizationHeader() async throws {
        URLProtocolMock.requestHandler = { request in
            XCTAssertEqual(request.httpMethod, "GET")
            XCTAssertEqual(request.value(forHTTPHeaderField: "Authorization"), "Bearer token")
            XCTAssertEqual(request.url?.path, "/api/users/me")

            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 200,
                httpVersion: nil,
                headerFields: nil
            )!
            return (response, Self.userResponseData)
        }

        let client = makeClient()
        let user = try await client.getCurrentUser(token: "token")

        XCTAssertEqual(user.email, "admin@local.dev")
    }

    func testUnauthorizedReturnsAPIErrorUnauthorized() async {
        URLProtocolMock.requestHandler = { request in
            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 401,
                httpVersion: nil,
                headerFields: nil
            )!
            return (response, Data())
        }

        let client = makeClient()

        do {
            _ = try await client.getCurrentUser(token: "token")
            XCTFail("Expected unauthorized error")
        } catch let error as APIError {
            XCTAssertEqual(error, .unauthorized)
        } catch {
            XCTFail("Unexpected error type")
        }
    }

    func testServerErrorReturnsAPIErrorServerMessage() async {
        URLProtocolMock.requestHandler = { request in
            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 500,
                httpVersion: nil,
                headerFields: nil
            )!
            return (response, Self.errorResponseData)
        }

        let client = makeClient()

        do {
            _ = try await client.getCurrentUser(token: "token")
            XCTFail("Expected server error")
        } catch let error as APIError {
            switch error {
            case .server(let message):
                XCTAssertEqual(message, "Server error")
            default:
                XCTFail("Expected server error")
            }
        } catch {
            XCTFail("Unexpected error type")
        }
    }

    func testDecodingErrorReturnsAPIErrorDecodingFailed() async {
        URLProtocolMock.requestHandler = { request in
            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 200,
                httpVersion: nil,
                headerFields: nil
            )!
            return (response, Data("invalid".utf8))
        }

        let client = makeClient()

        do {
            _ = try await client.getCurrentUser(token: "token")
            XCTFail("Expected decoding error")
        } catch let error as APIError {
            XCTAssertEqual(error, .decodingFailed)
        } catch {
            XCTFail("Unexpected error type")
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
