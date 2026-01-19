import XCTest
@testable import ios

final class APIErrorTests: XCTestCase {
    func testUnauthorizedMessage() {
        XCTAssertEqual(APIError.unauthorized.userFacingMessage, "Invalid email or password.")
    }

    func testServerMessageUsesDetail() {
        XCTAssertEqual(APIError.server(message: "Service unavailable").userFacingMessage, "Service unavailable")
    }

    func testFallbackMessageForGenericErrors() {
        XCTAssertEqual(APIError.invalidResponse.userFacingMessage, "Something went wrong. Please try again.")
    }
}
