import Observation
import SwiftUI

struct LoginView: View {
    @State private var viewModel: LoginViewModel

    init(sessionStore: SessionStore) {
        _viewModel = State(initialValue: LoginViewModel(sessionStore: sessionStore))
    }

    var body: some View {
        @Bindable var viewModel = viewModel

        ScrollView {
            VStack(spacing: 28) {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Nova 🌟")
                        .font(.largeTitle)
                        .bold()
                    Text("Welcome back")
                        .font(.title3)
                        .bold()
                    Text("Sign in with your account.")
                        .foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)

                VStack(spacing: 16) {
                    VStack(spacing: 12) {
                        LabeledField(title: "Email") {
                            TextField("Email", text: $viewModel.email)
                                .textContentType(.emailAddress)
                                .keyboardType(.emailAddress)
                                .textInputAutocapitalization(.never)
                                .autocorrectionDisabled()
                        }

                        LabeledField(title: "Password") {
                            SecureField("Password", text: $viewModel.password)
                                .textContentType(.password)
                        }
                    }

                    if let errorMessage = viewModel.errorMessage {
                        Text(errorMessage)
                            .foregroundStyle(.red)
                            .multilineTextAlignment(.center)
                    }

                    Button {
                        Task {
                            await viewModel.submit()
                        }
                    } label: {
                        if viewModel.isSubmitting {
                            ProgressView()
                                .frame(maxWidth: .infinity)
                        } else {
                            Text("Sign In")
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(!viewModel.canSubmit || viewModel.isSubmitting)
                }
                .padding(20)
                .background(.ultraThinMaterial)
                .clipShape(.rect(cornerRadius: 22))
            }
            .padding(24)
        }
        .scrollIndicators(.hidden)
        .navigationTitle("")
        .navigationBarTitleDisplayMode(.inline)
    }
}

private struct LabeledField<Field: View>: View {
    let title: String
    @ViewBuilder let field: Field

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.footnote)
                .foregroundStyle(.secondary)
            field
                .padding(.vertical, 10)
                .padding(.horizontal, 12)
                .background(.background)
                .clipShape(.rect(cornerRadius: 12))
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .strokeBorder(.quaternary)
                )
        }
    }
}

#Preview {
    let store = SessionStore(apiClient: .live(), tokenStore: InMemoryTokenStore())
    store.status = .unauthenticated
    return NavigationStack {
        LoginView(sessionStore: store)
    }
}
