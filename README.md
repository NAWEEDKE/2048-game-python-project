# 🎮 2048 Game (Python + Pygame)

## 📌 Description

This is an advanced version of the classic **2048 game** built using Python and Pygame.
It includes modern UI elements, sound effects, themes, and special power-ups to enhance gameplay.

---

## 🚀 Features

### 🎯 Core Gameplay

* Classic 2048 sliding tile mechanics
* Smooth animations and responsive controls
* Score and Best Score tracking (saved locally)

### 🎨 Themes

* Default Theme
* Ocean Theme 🌊
* Retro Theme 🟢

### 🔥 Power-Ups

* 💣 **Bomb** → Remove any tile
* 🔀 **Shuffle** → Randomly rearrange tiles

### 🎮 UI & Experience

* Interactive buttons with hover effects
* Pause menu with options:

  * Resume game
  * Change theme
  * Reset best score
  * Return to main menu

### 🔊 Sound Effects

* Move sound
* Click sound
  *(Auto-disabled if sound files are missing)*

---

## 🛠️ Technologies Used

* Python
* Pygame

---

## 📂 Project Structure

```bash
.
├── main.py
├── move.wav
├── click.wav
└── 2048_best_score.json  (auto-generated)
```

---

## ▶️ How to Run

### 1. Install dependencies

```bash
pip install pygame
```

### 2. Run the game

```bash
python main.py
```

---

## 🎮 Controls

| Key         | Action        |
| ----------- | ------------- |
| ⬅️ ➡️ ⬆️ ⬇️ | Move tiles    |
| ESC         | Pause Menu    |
| Mouse Click | Use power-ups |

---

## 🧠 Game Logic Highlights

* Dynamic board rotation for movement logic
* Random tile generation (2 or 4)
* Game-over detection
* Persistent best score using JSON file

---

## 📸 Screenshots

*(Add your screenshots here for better presentation)*

---

## 🎥 Demo

*(Optional: Add gameplay video link here)*

---

## 💡 Future Improvements

* Add animations for tile merging
* Online leaderboard
* Mobile version
* More power-ups

---

## 👨‍💻 Author

**Your Name**

---

## ⭐ Show Your Support

If you like this project:

* Star ⭐ the repository
* Fork it 🍴
* Share it 🚀
