//
//  ContentView.swift
//  ios
//
//  Created by M on 1/19/26.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            Image(systemName: "gearshape.2.fill")
                .imageScale(.large)
                .foregroundStyle(.tint)
            Text("Hello, Nova 🌟")
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
