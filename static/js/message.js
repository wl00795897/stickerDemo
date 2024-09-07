let socketio = io();

const messages = document.getElementById("messages");
const header = document.getElementById("header");
const userName = header.getAttribute('userName');

const createMessage = (name, msg, type) => {
    console.log(userName);
    if(type === "connection"){
        const content = `
        <div class="connection">
            ${name} ${msg} @ ${new Date().toLocaleString()}
        </div>
        `;
        messages.innerHTML += content;
    }
    else if(name === userName){
        const content = `
        <div class="ownNameDisplay">
            <strong>${name}</strong>
        </div>
        <div class="ownMessageContent">
            <p>${msg}</p>
        </div>
        `;
        messages.innerHTML += content;
    }
    else{
        const content = `
        <div class="nameDisplay">
            <strong>${name}</strong>
        </div>
        <div class="messageContent">
            <p>${msg}</p>
        </div>
        `;
        messages.innerHTML += content;
    }
};

const createImage = (name, imageEncoded) => {
    image = imageEncoded.data
    if (name === userName){
        const content = `
        <div class="ownNameDisplay">
            <strong>${name}</strong> sent a sticker
        </div>
        <img src="data:image/jpeg;base64,${image}" class="ownStickerChat"/>
        `;
        messages.innerHTML += content;
    }else{
        const content = `
        <div class="nameDisplay">
            <strong>${name}</strong> sent a sticker
        </div>
        <img src="data:image/jpeg;base64,${image}" class="stickerChat"/>
        `;
        messages.innerHTML += content;
    }


  };

socketio.on("message", (data) => {
    createMessage(data.name, data.message, data.type);

});

socketio.on("image", (data) => {
    createImage(data.name, data.image_data);
});

const sendMessage = () => {
    const message = document.getElementById("message");
    if (message.value == "")
        return;
    socketio.emit("message", { data: message.value });
    message.value = "";
};



