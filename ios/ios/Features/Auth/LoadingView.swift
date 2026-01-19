import SwiftUI

struct LoadingView: View {
    var body: some View {
        VStack(spacing: 16) {
            Text("Nova 🌟")
                .font(.largeTitle)
                .bold()
            ProgressView()
            Text("Loading…")
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding(24)
    }
}

#Preview {
    LoadingView()
}
