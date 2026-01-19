import Observation
import SwiftUI

struct SessionRootView: View {
    @Bindable var sessionStore: SessionStore

    var body: some View {
        NavigationStack {
            switch sessionStore.status {
            case .checking:
                LoadingView()
            case .unauthenticated:
                LoginView(sessionStore: sessionStore)
            case .authenticated(let user):
                UserHomeView(user: user) {
                    sessionStore.logout()
                }
            case .error(let message):
                SessionErrorView(message: message) {
                    Task {
                        await sessionStore.restoreSession()
                    }
                }
            }
        }
    }
}

#Preview {
    let store = SessionStore(apiClient: .live(), tokenStore: InMemoryTokenStore())
    store.status = .unauthenticated
    return SessionRootView(sessionStore: store)
}
