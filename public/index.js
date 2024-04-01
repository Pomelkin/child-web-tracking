const output = document.getElementById('output');
const outCtx = output.getContext('2d');
const videoCanvas = document.getElementById('video');
const ctx = videoCanvas.getContext('2d');
const input = document.getElementById('input');
// const ws = new WebSocket('ws://ontollm.semograph.com:28080/ws');
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
    }, 500)
}
function captureFrame () {
    const imageData = ctx.getImageData(0, 0, videoCanvas.width, videoCanvas.height);
    const dataURL = videoCanvas.toDataURL().split(',')[1];
    axios.post('http://ontollm.semograph.com:28080/frame', { b64_frame: dataURL})
    .then(res => {
        drawImage(res.data.b64_frame);
    })
}

// ws.onmessage = (event) => {
//     const base64 = 'data:image/jpeg;base64,' + event.data;
//     const img = new Image();
//     img.src = base64;
//     img.onload = () => {
//         outCtx.drawImage(img, 0, 0, output.width, output.height);
//     }
// }
function drawImage(base64){
    const newbase64 = 'data:image/jpeg;base64,' + base64;
    const img = new Image();
    img.src = newbase64;
    img.onload = () => {
        outCtx.drawImage(img, 0, 0, output.width, output.height);
    }
}
