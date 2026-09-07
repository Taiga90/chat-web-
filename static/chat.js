const socket = io();

socket.on("message", (data) => {
    const box = document.createElement("div");
    box.classList.add("message-box");

    if (data.user === username) {
        box.classList.add("message-self");
    }

    box.textContent = data.user + ": " + data.text;
    document.getElementById("messages").appendChild(box);
});

socket.on("image", (data) => {
    const box = document.createElement("div");
    box.classList.add("message-box");

    if (data.user === username) {
        box.classList.add("message-self");
    }

    const img = document.createElement("img");
    img.src = data.url;
    img.classList.add("message-image");

    box.appendChild(img);
    document.getElementById("messages").appendChild(box);
});

function sendMsg() {
    const text = document.getElementById("msg").value;
    socket.send({ user: username, text: text });
    document.getElementById("msg").value = "";
}

function sendImage() {
    const fileInput = document.getElementById("imageInput");
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append("image", file);

    fetch("/upload", {
        method: "POST",
        body: formData
    });

    fileInput.value = "";
}
