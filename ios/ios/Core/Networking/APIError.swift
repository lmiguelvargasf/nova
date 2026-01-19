import Foundation

enum APIError: Error, LocalizedError, Hashable {
    case invalidResponse
    case decodingFailed
    case unauthorized
    case server(message: String?)
    case network

    var errorDescription: String? {
        userFacingMessage
    }

    var userFacingMessage: String {
        switch self {
        case .unauthorized:
            return "Invalid email or password."
        case .server(let message):
            return message ?? "Something went wrong. Please try again."
        case .invalidResponse, .decodingFailed, .network:
            return "Something went wrong. Please try again."
        }
    }
}
