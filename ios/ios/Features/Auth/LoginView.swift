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
            VStack(spacing: 24) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Nova 🌟")
                        .font(.largeTitle)
                        .bold()
                    Text("Welcome back")
                        .font(.title2)
                        .bold()
                    Text("Use your account to continue.")
                        .foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)

                VStack(spacing: 16) {
                    VStack(spacing: 12) {
                        TextField("Email", text: $viewModel.email)
                            .textContentType(.emailAddress)
                            .keyboardType(.emailAddress)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()
                            .textFieldStyle(.roundedBorder)

                        SecureField("Password", text: $viewModel.password)
                            .textContentType(.password)
                            .textFieldStyle(.roundedBorder)
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
                .background(.thinMaterial)
                .clipShape(.rect(cornerRadius: 20))
            }
            .padding(24)
        }
        .scrollIndicators(.hidden)
        .navigationTitle("")
        .navigationBarTitleDisplayMode(.inline)
    }
}
