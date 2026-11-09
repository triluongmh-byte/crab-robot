import Foundation
import Vision
import ImageIO
let cases = ["WIFI:T:nopass;S:CuaRobot-1234;;", "http://192.168.1.245/"]
for i in 1...2 {
    let url = URL(fileURLWithPath: CommandLine.arguments[1] + "/qr\(i).png")
    let req = VNDetectBarcodesRequest()
    req.symbologies = [.qr]
    try VNImageRequestHandler(url: url).perform([req])
    let decoded = req.results?.first?.payloadStringValue
    if decoded != cases[i-1] { fputs("QR decode mismatch: \(String(describing: decoded))\n", stderr); exit(1) }
}
print("PASS: Apple Vision independently decoded both QR payloads at actual LCD scale")
