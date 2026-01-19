import Foundation

struct APIClient: Sendable {
    let baseURL: URL
    let session: URLSession

    static func live(configuration: APIConfiguration = .load()) -> APIClient {
        APIClient(baseURL: configuration.baseURL, session: .shared)
    }

    func login(email: String, password: String) async throws -> LoginResponse {
        let requestBody = LoginRequest(email: email, password: password)
        let request = try makeRequest(path: "api/auth/login", method: "POST", token: nil, body: requestBody)
        return try await send(request)
    }

    func getCurrentUser(token: String) async throws -> User {
        let request = try makeRequest(path: "api/users/me", method: "GET", token: token)
        return try await send(request)
    }

    private func makeRequest(
        path: String,
        method: String,
        token: String?
    ) throws -> URLRequest {
        let url = baseURL.appending(path: path)
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        if let token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        return request
    }

    private func makeRequest<T: Encodable>(
        path: String,
        method: String,
        token: String?,
        body: T?
    ) throws -> URLRequest {
        var request = try makeRequest(path: path, method: method, token: token)
        if let body {
            let encoder = JSONEncoder()
            encoder.keyEncodingStrategy = .convertToSnakeCase
            request.httpBody = try encoder.encode(body)
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }
        return request
    }

    private func send<T: Decodable>(_ request: URLRequest) async throws -> T {
        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw APIError.network
        }

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        if httpResponse.statusCode == 401 {
            throw APIError.unauthorized
        }

        guard (200..<300).contains(httpResponse.statusCode) else {
            let decoder = JSONDecoder()
            decoder.keyDecodingStrategy = .convertFromSnakeCase
            let errorResponse = try? decoder.decode(APIErrorResponse.self, from: data)
            throw APIError.server(message: errorResponse?.detail)
        }

        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decodingFailed
        }
    }
}

private struct APIErrorResponse: Decodable {
    let detail: String?
}
