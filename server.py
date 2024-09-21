from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_socketio import join_room, leave_room, send, emit, SocketIO
from flask_cors import CORS
import random
import string
import io
from base64 import encodebytes
from PIL import Image, ImageFont, ImageDraw
from diffusers import StableDiffusionXLPipeline, AutoencoderKL
import os
import torch
from transformers import pipeline
from pprint import pprint
import time

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app)
rooms = {}
# For CUDA
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=0)
# For MacOS
# classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix").to(torch.float16)
loras = [
    {"name": "otter", "checkpoint": "checkpoint-3000/pytorch_lora_weights.safetensors"},
    {"name": "tiger", "checkpoint": "checkpoint-1200/pytorch_lora_weights.safetensors"},
    {"name": "rabbit", "checkpoint": "checkpoint-2400/pytorch_lora_weights.safetensors"},
    {"name": "pig", "checkpoint": "checkpoint-3500/pytorch_lora_weights.safetensors"}
]
candidate_labels = ['Happy', 'Sad', 'Angry', 'Tired', 'Hello', 'Congratulation', 'Thanks']

def code_gen(length):
    code = ''.join(random.choices(string.digits, k=length))
    if code not in rooms:
        return code
    else:
        return code_gen(length)

def get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r') # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='JPEG') # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64
    return encoded_img

@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", code=code, name=name)
        
        room = code
        if create != False:
            room = code_gen(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    name = session.get("name")
    if room is None or name is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, name=name, messages=rooms[room]["messages"])

@app.route("/api/getStickers", methods=["POST"])
def getStickers():
    if request.method == "POST":
        data = request.get_json()
        pfc = data.get("input")
        if len(pfc.split()) == 1:
            prompt_word = pfc
            print(f"Received input from client: {prompt_word}")
        else:
            result = classifier(pfc, candidate_labels)
            prompt_word = result['labels'][0]
            print(f"Received input from client: {pfc}")
            print(f"After ZSL: {prompt_word}")
        # prompt_animal = "otter"
        # result = classifier(data.get("input"), candidate_labels)
        # prompt_word = result['labels'][0]

        # vae = AutoencoderKL.from_pretrained(
        # "madebyollin/sdxl-vae-fp16-fix"
        # ).to(torch.float16)
        # loras = [
        #     {"name": "otter", "checkpoint": "checkpoint-3000/pytorch_lora_weights.safetensors"},
        #     {"name": "tiger", "checkpoint": "checkpoint-1200/pytorch_lora_weights.safetensors"},
        #     {"name": "rabbit", "checkpoint": "pytorch_lora_weights.safetensors"},
        #     {"name": "pig", "checkpoint": "pytorch_lora_weights.safetensors"}
        # ]
        start = time.time()
        for i in range (4):
            pipeline = StableDiffusionXLPipeline.from_pretrained("stabilityai/sdxl-turbo", vae=vae, torch_dtype=torch.float16).to("cuda") 
            pipeline.enable_xformers_memory_efficient_attention()
            # pipeline = StableDiffusionXLPipeline.from_pretrained("stabilityai/sdxl-turbo", vae=vae, torch_dtype=torch.float16).to("mps")
            selected_loras = random.sample(loras, k=2)
            lora = []
            for selected_lora in selected_loras:
                pipeline.load_lora_weights(
                    f"dm-sticker/sdxl-turbo-lora-{selected_lora['name']}-sticker", 
                    weight_name=selected_lora["checkpoint"], 
                    adapter_name=selected_lora["name"]
                )
                lora.append(selected_lora["name"])
            # print(((i+1) * random.randint(1, 10000)) % 2)
            prompt_animal = lora[(random.randint(1, 10000)) % 2]
            print(f"merged lora: {lora}, prompt_animal: {prompt_animal}")
            # activate both LoRAs and set adapter weights
            pipeline.set_adapters(lora, adapter_weights=[0.5, 0.5])

            # fuse LoRAs and unload weights
            pipeline.fuse_lora(adapter_names = lora, lora_scale=1.0)
            pipeline.unload_lora_weights()

            # torch.compile
            # pipeline.unet.to(memory_format=torch.channels_last)
            # pipeline.unet = torch.compile(pipeline.unet, mode="reduce-overhead", fullgraph=True)
            default_prompt = "dm-sticker, furious, pissed off"
            prompt = default_prompt + ", " + prompt_animal + ", " + prompt_word
            negative_prompt = "blank eyes, alphabet, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name,(deformed, distorted, disfigured:1.3), poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, (mutated hands and fingers:1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation, bad art, worst quality, worst details, poorly drawn face, fused face, cloned face, ugly eyes, ((imperfect eyes)), deformed pupils, deformed iris, extra eyes, oversized eyes, extra crus, fused crus, extra thigh, fused thigh, missing fingers, extra fingers, elongated fingers, amputation, disconnected limbs, artist signature, upside down, asymmetrical eyes"

            image = pipeline(prompt = prompt,negative_prompt=negative_prompt, num_inference_steps=12, guidance_scale=2.0, height = 320, width = 320).images[0]
            img_w, img_h = image.size
            print("New enabled")
            image.save(f"./{i + 1}.jpg") 
            # layer = Image.new('RGB', (640,640), (255,255,255))
            # bg_w, bg_h = layer.size
            # offset = ((bg_w - img_w) // 2, bg_w - img_w)
            # layer.paste(image, offset)
            # # layer.save('./ok1.jpg')
            # font = ImageFont.truetype('NerkoOne-Regular.ttf', 150) 
            # draw = ImageDraw.Draw(layer)     
            # draw.text((layer.size[0]//2, 32), prompt_word, anchor='mt', fill=(0, 0, 0), font=font)  
            # layer.save(f"./{i + 1}.jpg")  
    end = time.time()
    print(end - start)
    result = ["1.jpg", "2.jpg", "3.jpg", "4.jpg"]
    encoded_imges = []
    for image_path in result:
        encoded_imges.append(get_response_image(image_path))
    return jsonify({'images': encoded_imges})


@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"],
        "type": "chat"
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("image")
def image(data):
    room = session.get("room")
    if room not in rooms:
        return 
    content = {
        "name": session.get("name"),
        "image_data": data,
        "type": "image"
    }
    emit('image', content, room=room)

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    join_room(room)
    content = {
        "name": name,
        "message": "enter the room",
        "type": "connection"
    }
    send(content, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    content = {
        "name": name,
        "message": "leave the room",
        "type": "connection"
    }
    send(content, to=room)
    print(f"{name} has left the room {room}")

if __name__ == "__main__":
    socketio.run(app, debug=True, port="5002")