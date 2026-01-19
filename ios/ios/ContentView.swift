//
//  ContentView.swift
//  ios
//
//  Created by M on 1/19/26.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        SessionRootView()
    }
}

#Preview {
    let store = SessionStore(apiClient: .live(), tokenStore: InMemoryTokenStore())
    store.status = .unauthenticated
    return ContentView()
        .environment(store)
}
