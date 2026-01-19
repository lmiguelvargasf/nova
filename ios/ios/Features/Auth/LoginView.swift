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
            VStack(spacing: 20) {
                VStack(spacing: 8) {
                    Text("Welcome back")
                        .font(.title)
                        .bold()
                    Text("Sign in to your Nova account.")
                        .foregroundStyle(.secondary)
                }

                VStack(spacing: 16) {
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
            .padding()
        }
        .scrollIndicators(.hidden)
        .navigationTitle("Sign In")
    }
}
