//
//  Requests.swift
//  APP
//
//  Created by Omar Elshobky on 14/10/2023.
//
//

import Foundation
import SwiftUI

struct Requests {
    let parent : ContentView
    
    func postReq(path : String) async throws -> () {
        let endpoint = "http://127.0.0.1:8000/paths/"
        guard let url = URL(string: endpoint) else {throw my_error.invalidUrl}
        
        var request = URLRequest(url : url)
        request.httpMethod = "POST"
        request.setValue("application/json",forHTTPHeaderField: "Content-Type")
        let body: [String: AnyHashable] = [
            "id" : 5,
            "src_path" : path
        ]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body,options : .fragmentsAllowed)
        
        let task = URLSession.shared.dataTask(with: request) {
            data,_,error in guard let data = data , error == nil else{return}
            do{
                let decoder = JSONDecoder()
                decoder.keyDecodingStrategy = .convertFromSnakeCase
                let p =  try decoder.decode(Path.self, from : data)
                self.parent.imagePath = p.srcPath
                self.parent.url = URL(string: p.srcPath)
            }
            catch{
                print("error in decoding !!")
            }
        }
        task.resume()
    }
        
    struct Path: Codable {
        let id: Int
        let srcPath:String
    }
}
enum my_error : Error {
    case invalidUrl
}
