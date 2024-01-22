//
//  ContentView.swift
//  BasketballDetection
//
//  Created by Omar Elshobky on 14/10/2023.
//
// allow only jpg files

import SwiftUI
import CoreML

struct ContentView: View {
    
    @State var imagePath : String?
    @State var imageSelected : Bool = false
    @State var showAlert1 : Bool = false
    @State var showAlert2 : Bool = false
    @State var url : URL?
    @State var detected : Bool = false
    
    var body: some View {
        
        ZStack{
            
            VStack{
                Text("Basketball Detection")
                    .foregroundColor(.white)
                    .fontWeight(.semibold)
                    .font(.title)
                Spacer()
                if (url != nil){
                    if let nsImage = NSImage(contentsOf: url! ) {
                        Image(nsImage: nsImage)
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                        
                    }
                }
                Spacer()
                HStack{
                    Spacer()
                    /// UPLOAD PIC BUTTON
                    Button("Upload Picture",systemImage:"plus.square.fill",
                           action: {
                        let panel = NSOpenPanel()
                        panel.allowsMultipleSelection = false
                        panel.canChooseDirectories = true
                        if panel.runModal() == .OK {
                            imagePath = panel.url?.absoluteString ?? "<none>"
                            imageSelected = true
                            detected = false
                            self.url = URL(string: imagePath!)
                        }
                    })
                    .cornerRadius(20)
                    
                    Spacer()
                    
                    // RUN DETECTION BUTTON
                    Button("Run Detection", systemImage: "magnifyingglass.circle.fill", action: {
                        if imageSelected && !detected{
                            Task{
                                do{
                                    let r = Requests(parent: self)
                                    _ = try await r.postReq(path : imagePath!)
                                    print(self.imagePath!)
                                    detected = true
                                } catch{ print("error") }
                            }
                        }
                        else if (imageSelected) {
                            showAlert2 = true
                        }
                        else{
                            showAlert1 = true
                        }
                    })
                    .cornerRadius(20)
                    
                    .alert("Are you kidding??\nNO image selected !", isPresented: $showAlert1) {
                                Button("OK", role: .cancel) { }
                    }
                    .dialogIcon(Image(systemName: "questionmark.folder.fill"))
                    
                    .alert("you already ran detection\nchoose another one", isPresented: $showAlert2){
                                Button("OK", role: .cancel) { }
                    }
                    .dialogIcon(Image(systemName: "exclamationmark.circle"))
                    Spacer()
                }
                .padding()
                .buttonStyle(.bordered)
            }
        }
    }
}
#Preview {
    ContentView()
}
