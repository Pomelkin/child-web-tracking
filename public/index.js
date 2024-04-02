const output = document.getElementById('output');
const outCtx = output.getContext('2d');
const videoCanvas = document.getElementById('video');
const ctx = videoCanvas.getContext('2d');
const input = document.getElementById('input');
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
    const dataURL = videoCanvas.toDataURL().split(',')[1];
    console.log(dataURL);
    ws.send(dataURL);
}

ws.onmessage = (event) => {
    drawImage(event.data);
}
function drawImage(data){
    outCtx.clearRect(0, 0, videoCanvas.width, videoCanvas.height);
    console.log(data)
    const bboxes =  JSON.parse(data).bboxes;
    outCtx.drawImage(input, 0, 0, videoCanvas.width, videoCanvas.height);

    for(let i = 0; i < bbox.length; i++){
        const bbox = bboxes[i];
        
        outCtx.beginPath();
        outCtx.lineWidth = "2";
        outCtx.strokeStyle = 'red';
        outCtx.rect(bbox[0], bbox[1], bbox[2], bbox[3]);
        outCtx.stroke();
        
    }
    console.log(bboxes)

    
}
