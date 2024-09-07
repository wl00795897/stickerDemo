const stickerInput = document.getElementById("sticker-input");
const ideaButton = document.getElementById("idea-btn");
const stickerContainer = document.getElementById("sticker-container");

let prompt = "";
let array = [];

const sendInput = async () => {
  try {
    const response = await fetch("http://localhost:5002/api/getStickers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: prompt })
    });
    const data = await response.json();
    console.log(data.images);
    array = data.images;
    stickerDisplay();
  } catch (error) {
    console.error("Error sending and fetching data to server:", error);
  }
};

const sendImage = (image) => {
    if (image == "")
      return;
    // console.log(image)
    socketio.emit("image", { data: image });
    image = "";
  };

const stickerDisplay = () => {
  stickerContainer.innerHTML = "";
  array.forEach((image, index) => {
    const imgElement = document.createElement("img");
    imgElement.src = `data:image/jpeg;base64,${image}`;
    imgElement.classList.add("stickerGenPhoto");
    imgElement.addEventListener("click", () => {
      sendImage(image);
    });
    stickerContainer.appendChild(imgElement);
  });
};

stickerInput.addEventListener("input", (e) => {
  prompt = e.target.value;
});

ideaButton.addEventListener("click", sendInput);