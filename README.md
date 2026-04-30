# DriveGuard-VisionAI
An AI-powered driver monitoring system that detects drowsiness in real time using computer vision and alerts drivers to prevent accidents.
<h1 align="center">🚗 DriveGuard-VisionAI</h1>

<p align="center">
  👁️ Real-Time Driver Drowsiness Detection using AI <br>
  ⚡ Stay Awake. Stay Safe.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AI-Computer%20Vision-blue?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Python-3.9-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/OpenCV-Enabled-orange?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge"/>
</p>

---

## 🎥 Demo Preview
<p align="center">
  <img src="https://media.giphy.com/media/l0HlBO7eyXzSZkJri/giphy.gif" width="500"/>
</p>

---

## 🧠 About the Project

🚗 **DriveGuard-VisionAI** is an AI-powered system that monitors drivers in real-time using computer vision to detect signs of drowsiness like:

- 😴 Eye closure  
- 😮 Yawning  
- 🤕 Head dropping  

⚠️ When fatigue is detected, the system instantly triggers an **alert/alarm** to prevent accidents.

---

## ⚙️ Features

✨ Real-time face detection  
👁️ Eye Aspect Ratio (EAR) tracking  
😴 Drowsiness detection  
🔊 Instant alert system  
📹 Live webcam monitoring  

---

## 🛠️ Tech Stack

- 🐍 Python  
- 👁️ OpenCV  
- 🤖 MediaPipe / Dlib  
- 🔢 NumPy  
- 🔊 Pygame  

---

## 🚀 How It Works

```mermaid
flowchart LR
A[Camera Input] --> B[Face Detection]
B --> C[Eye Tracking]
C --> D[EAR Calculation]
D --> E{Eyes Closed?}
E -->|Yes| F[Trigger Alarm 🚨]
E -->|No| G[Normal State ✅]
📦 Installation
git clone https://github.com/yourusername/DriveGuard-VisionAI.git
cd DriveGuard-VisionAI
pip install -r requirements.txt
python main.py
🧪 Future Improvements
📱 Mobile alerts (SMS / App)
🧠 Deep learning model integration
📊 Driver fatigue dashboard
🌙 Night vision support
📸 Screenshots
<p align="center"> <img src="https://via.placeholder.com/400x250.png?text=Detection+View"/> <img src="https://via.placeholder.com/400x250.png?text=Alert+System"/> </p>
🤝 Contributing

Contributions are welcome!
Feel free to fork this repo and submit a pull request 🚀

📜 License

This project is licensed under the MIT License.

<p align="center"> 💡 Built with passion for safer roads 🚗❤️ </p>
