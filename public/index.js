const output = document.getElementById('output');
const videoCanvas = document.getElementById('video');
const ctx = videoCanvas.getContext('2d');
const input = document.getElementById('input');
const ws = new WebSocket('ws://localhost:8000');
videoCanvas.width = 640;
videoCanvas.height = 480;
navigator.mediaDevices.getUserMedia({ video: true, audio: false })
.then(stream => {
    input.srcObject = stream;
    onVideo();
    console.log(input.videoWidth, input.videoHeight);
})

function onVideo(){
    setInterval(() => {
        ctx.drawImage(input, 0, 0, videoCanvas.width, videoCanvas.height);
        captureFrame();
    }, 100)
}
function captureFrame () {
    const imageData = ctx.getImageData(0, 0, videoCanvas.width, videoCanvas.height);
    console.log(imageData);
    ws.send(videoCanvas.toDataURL());
}