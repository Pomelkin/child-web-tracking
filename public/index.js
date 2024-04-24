const output = document.getElementById('output');
const outCtx = output.getContext('2d');
const videoCanvas = document.getElementById('video');
const ctx = videoCanvas.getContext('2d');
const input = document.getElementById('input');
const num = document.getElementById('number');
const info = document.getElementById('info');
// const ws = new WebSocket('ws://ontollm.semograph.com:28080/ws');
const ws = new WebSocket('ws://localhost:8000/ws');

videoCanvas.width = 640;
videoCanvas.height = 480;
output.width = 640;
output.height = 480;
navigator.mediaDevices.getUserMedia({ video: true, audio: false })
.then(stream => {
    input.srcObject = stream;
    onVideo();
})

function onVideo(){
    setInterval(() => {
        ctx.drawImage(input, 0, 0, videoCanvas.width, videoCanvas.height);
        captureFrame();
    }, 250)
}
function captureFrame () {
    const n = +num.value;
    const dataURL = videoCanvas.toDataURL().split(',')[1];
    const data = {
        task: n,
        base64_img: dataURL
    }
    console.log(data)
    ws.send(JSON.stringify(data));
}

ws.onmessage = (event) => {
    info.innerText = JSON.parse(event.data);
    drawImage();
}
function drawImage(){
    outCtx.drawImage(input, 0, 0, videoCanvas.width, videoCanvas.height);    
}
