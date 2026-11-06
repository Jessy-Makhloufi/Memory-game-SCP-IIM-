import tkinter as tk
from tkinter import Image, PhotoImage, messagebox, ttk, simpledialog
import random
import json
import os
import time

# Fichiers de sauvegarde
SAVE_DIR = "memory_saves"
SCORES_FILE = "memory_scores.json"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Palette de couleurs - Thème FONDATION SCP (Sombre & High-Tech)
BG_DARK = "#0D1117"          # Noir/Gris anthracite très sombre (Interface Terminal SCP)
BG_CARD_BACK = "#161B22"     # Dos de carte sombre style coffre fort
BG_CARD_FRONT = "#21262D"    # Révélation d'entité
TEXT_COLOR = "#C9D1D9"       # Texte clair style moniteur
ACCENT_BLUE = "#58A6FF"      # Bleu accès sécurisé
ACCENT_GREEN = "#2EA043"     # Vert confinement réussi / Point marqué
ACCENT_RED = "#DA3633"       # Rouge alerte brèche SCP
CARD_BORDER = "#30363D"      # Bordure de carte renforcée


scp_087 = PhotoImage(file="scp_087.png")  # Image de fond pour le menu principal
scp_096 = PhotoImage(file="scp_096.png")
scp_692 = PhotoImage(file="scp_692.png")
scp_999 = PhotoImage(file="scp_999.png")
scp_173 = PhotoImage(file="scp_173.png")

Image.config(scp_087, width=80, height=80)
Image.config(scp_096, width=80, height=80)
Image.config(scp_692, width=80, height=80)
Image.config(scp_999, width=80, height=80)
Image.config(scp_173, width=80, height=80)

# Symboles / Identifiants d'Anomalies SCP
EMOJIS = [
    scp_087, scp_096, scp_692, scp_999, scp_173,
    "💀", "🧬", "🔐", "🛸", "💉", "🧪", "🛰️", "🤖", "👻", "⚡"]


class MemoryGameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SCP FOUNDATION - Protocol Memory 05")
        self.geometry("920x770")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)

        # Variables du jeu
        self.score_p1 = 0
        self.score_p2 = 0
        self.moves = 0
        self.player1_name = "Agent Alpha"
        self.player2_name = "Agent Bravo"
        self.grid_rows = 5  # 5 lignes x 6 colonnes = 30 cartes
        self.grid_cols = 6
        self.cards = []
        self.selected_cards = []
        self.matched_pairs = 0
        self.total_pairs = (self.grid_rows * self.grid_cols) // 2
        self.is_animating = False

        # Container principal pour la navigation entre vues
        self.container = tk.Frame(self, bg=BG_DARK)
        self.container.pack(fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Initialisation des vues
        for PageClass in (MainMenu, GameScreen, HighScoresScreen, SettingsMenu):
            frame = PageClass(parent=self.container, controller=self)
            self.frames[PageClass] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainMenu)

    def toggle_fullscreen(self, value=None):
        """Active ou désactive le mode plein écran."""
        if value is None:
            is_full = not self.attributes("-fullscreen")
        else:
            is_full = value
        self.attributes("-fullscreen", is_full)

    def show_frame(self, page_class):
        """Affiche l'écran demandé."""
        frame = self.frames[page_class]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()

    def update_live_score(self, p1_name, p1_score, p2_name, p2_score, moves):
        """Enregistre séparément le score de chaque agent dans les archives."""
        scores = []
        if os.path.exists(SCORES_FILE):
            try:
                with open(SCORES_FILE, "r", encoding="utf-8") as f:
                    scores = json.load(f)
            except Exception:
                scores = []

        today_str = time.strftime("%H:%M - %d/%m")

        # Mise à jour ou ajout séparé pour chaque joueur
        players_data = [
            {"player": p1_name, "score": p1_score, "session_id": f"{p1_name}_{today_str}"},
            {"player": p2_name, "score": p2_score, "session_id": f"{p2_name}_{today_str}"}
        ]

        for p_data in players_data:
            found = False
            for entry in scores:
                if entry.get("session_id") == p_data["session_id"]:
                    entry["score"] = p_data["score"]
                    entry["moves"] = moves
                    found = True
                    break

            if not found:
                scores.append({
                    "session_id": p_data["session_id"],
                    "player": p_data["player"],
                    "score": p_data["score"],
                    "moves": moves,
                    "date": today_str
                })

        # Tri par score individuel décroissant, puis par nombre de tentatives
        scores = sorted(scores, key=lambda x: (-x["score"], x["moves"]))[:20]

        try:
            with open(SCORES_FILE, "w", encoding="utf-8") as f:
                json.dump(scores, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur mise à jour score en direct: {e}")


class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller

        # Layout responsive
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Titre principal style Terminal SCP
        title = tk.Label(
            self, text="🛡️ SCP FOUNDATION 🛡️", 
            font=("Consolas", 32, "bold"), 
            fg=ACCENT_RED, bg=BG_DARK
        )
        title.grid(row=1, column=0, pady=(20, 5))

        subtitle = tk.Label(
            self, text="[ CLASSIFIED - MEMORY CONTAINMENT PROTOCOL ]", 
            font=("Consolas", 13, "bold"), 
            fg=ACCENT_BLUE, bg=BG_DARK
        )
        subtitle.grid(row=2, column=0, pady=(0, 25))

        # Container des boutons centrés
        btn_container = tk.Frame(self, bg=BG_DARK)
        btn_container.grid(row=3, column=0, pady=10)

        # Style des boutons SCP
        btn_style = {
            "font": ("Consolas", 13, "bold"),
            "width": 28,
            "height": 2,
            "bd": 1,
            "relief": "flat",
            "cursor": "hand2",
            "activebackground": "#21262D",
            "activeforeground": "#FFFFFF"
        }

        btn_new = tk.Button(
            btn_container, text="▶ DEMARRER LA MISSION", 
            bg="#238636", fg="#FFFFFF", 
            command=self.start_new_game, **btn_style
        )
        btn_new.pack(pady=8)

        self.btn_load = tk.Button(
            btn_container, text="📂 RESTAURER LA SESSION", 
            bg="#1F6FEB", fg="#FFFFFF", 
            command=self.load_game, **btn_style
        )
        self.btn_load.pack(pady=8)

        btn_scores = tk.Button(
            btn_container, text="📊 ARCHIVES DES SCORES", 
            bg="#30363D", fg=TEXT_COLOR, 
            command=lambda: controller.show_frame(HighScoresScreen), **btn_style
        )
        btn_scores.pack(pady=8)

        btn_settings = tk.Button(
            btn_container, text="⚙️ PARAMETRES & SYSTEME", 
            bg="#30363D", fg=TEXT_COLOR, 
            command=lambda: controller.show_frame(SettingsMenu), **btn_style
        )
        btn_settings.pack(pady=8)

        btn_quit = tk.Button(
            btn_container, text="❌ FERMER LE TERMINAL", 
            bg="#DA3633", fg="#FFFFFF", 
            command=controller.quit, **btn_style
        )
        btn_quit.pack(pady=8)

    def on_show(self):
        """Vérifie si des sauvegardes existent pour activer/désactiver le bouton Continuer."""
        saves = [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
        if saves:
            self.btn_load.config(state="normal", bg="#1F6FEB")
        else:
            self.btn_load.config(state="disabled", bg="#161B22")

    def start_new_game(self):
        """Demande les pseudos des 2 agents (qui doivent être uniques) avant de lancer la mission."""
        p1 = simpledialog.askstring("Agent 1", "Identifiant Agent 1 :", parent=self)
        if p1 is None:
            return  # Annulation
        
        p1_name = p1.strip() if p1.strip() else "Agent Alpha"

        while True:
            p2 = simpledialog.askstring("Agent 2", "Identifiant Agent 2 :", parent=self)
            if p2 is None:
                return  # Annulation
            
            p2_name = p2.strip() if p2.strip() else "Agent Bravo"
            
            if p1_name.lower() == p2_name.lower():
                messagebox.showwarning(
                    "Identifiants Identiques", 
                    "Les deux agents doivent avoir des identifiants différents !",
                    parent=self
                )
            else:
                break

        self.controller.player1_name = p1_name
        self.controller.player2_name = p2_name

        game_screen = self.controller.frames[GameScreen]
        game_screen.start_new_game()
        self.controller.show_frame(GameScreen)

    def load_game(self):
        """Propose de choisir une sauvegarde parmi toutes les sauvegardes existantes."""
        saves = [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
        if not saves:
            messagebox.showinfo("Sauvegardes", "Aucune partie enregistrée trouvée.")
            return

        # Fenêtre de sélection de sauvegarde
        load_win = tk.Toplevel(self)
        load_win.title("Choisir une session")
        load_win.geometry("450x300")
        load_win.configure(bg=BG_DARK)
        load_win.transient(self)
        load_win.grab_set()

        lbl = tk.Label(load_win, text="SELECTIONNER UNE SAUVEGARDE :", font=("Consolas", 11, "bold"), fg=ACCENT_BLUE, bg=BG_DARK)
        lbl.pack(pady=10)

        listbox = tk.Listbox(load_win, font=("Consolas", 10), bg="#161B22", fg=TEXT_COLOR, selectbackground="#1F6FEB")
        listbox.pack(fill="both", expand=True, padx=15, pady=5)

        for s in saves:
            listbox.insert("end", s.replace(".json", ""))

        def confirm_load():
            sel = listbox.curselection()
            if not sel:
                return
            file_name = saves[sel[0]]
            load_win.destroy()
            game_screen = self.controller.frames[GameScreen]
            if game_screen.load_game_data(os.path.join(SAVE_DIR, file_name)):
                self.controller.show_frame(GameScreen)

        btn_confirm = tk.Button(load_win, text="CHARGER SESSION", font=("Consolas", 10, "bold"), bg="#1F6FEB", fg="#FFFFFF", bd=0, command=confirm_load, pady=6)
        btn_confirm.pack(pady=10)


class AnimatedCard(tk.Canvas):
    """Carte personnalisée avec animation de retournement style SCP."""
    def __init__(self, parent, symbol, on_click_callback, size=95):
        super().__init__(parent, width=size, height=size, bg=BG_DARK, highlightthickness=0)
        self.symbol = symbol
        self.on_click_callback = on_click_callback
        self.size = size
        self.is_flipped = False
        self.is_matched = False

        # Dessin initial du dos de la carte
        self.rect = self.create_rounded_rect(4, 4, size-4, size-4, radius=8, fill=BG_CARD_BACK, outline=CARD_BORDER, width=2)
        self.text = self.create_text(size//2, size//2, text="SCP", font=("Consolas", 18, "bold"), fill="#8B949E")

        self.bind("<Button-1>", self.handle_click)

    def create_rounded_rect(self, x1, y1, x2, y2, radius=8, **kwargs):
        """Dessine un rectangle carré à coins légèrement arrondis."""
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius,
                  x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2,
                  x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def handle_click(self, event):
        if not self.is_flipped and not self.is_matched:
            self.on_click_callback(self)

    def animate_flip(self, show_symbol, callback=None):
        """Animation de réduction puis d'expansion horizontale."""
        steps = 5
        delay = 15

        def shrink(step):
            if step >= 0:
                w = (self.size // 2) * (step / steps)
                self.coords(self.rect, self.get_contracted_coords(w))
                self.after(delay, lambda: shrink(step - 1))
            else:
                self.is_flipped = show_symbol
                if show_symbol:
                    self.itemconfig(self.rect, fill=BG_CARD_FRONT, outline=ACCENT_BLUE)
                    self.itemconfig(self.text, text=self.symbol, font=("Segoe UI Emoji", 30))
                else:
                    self.itemconfig(self.rect, fill=BG_CARD_BACK, outline=CARD_BORDER)
                    self.itemconfig(self.text, text="SCP", font=("Consolas", 18, "bold"), fill="#8B949E")
                expand(1)

        def expand(step):
            if step <= steps:
                w = (self.size // 2) * (step / steps)
                self.coords(self.rect, self.get_contracted_coords(w))
                self.after(delay, lambda: expand(step + 1))
            else:
                if callback:
                    callback()

        shrink(steps)

    def get_contracted_coords(self, current_w):
        center_x = self.size // 2
        radius = 8
        x1 = max(4, center_x - current_w)
        x2 = min(self.size - 4, center_x + current_w)
        y1 = 4
        y2 = self.size - 4

        return [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius,
                x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2,
                x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]

    def set_matched(self):
        """Marque l'anomalie comme neutralisée/confinée."""
        self.is_matched = True
        self.itemconfig(self.rect, fill="#132338", outline=ACCENT_GREEN, width=3)


class GameScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller

        # Barre d'informations style SCP Terminal
        self.top_bar = tk.Frame(self, bg="#161B22", padx=10, pady=8, highlightbackground="#30363D", highlightthickness=1)
        self.top_bar.pack(fill="x", pady=(10, 15), padx=15)

        self.score_p1_label = tk.Label(
            self.top_bar, text="Agent A: 0", 
            font=("Consolas", 11, "bold"), fg=ACCENT_BLUE, bg="#161B22"
        )
        self.score_p1_label.pack(side="left", padx=10)

        self.score_p2_label = tk.Label(
            self.top_bar, text="Agent B: 0", 
            font=("Consolas", 11, "bold"), fg="#D29922", bg="#161B22"
        )
        self.score_p2_label.pack(side="left", padx=10)

        self.turn_label = tk.Label(
            self.top_bar, text="Tour: J1", 
            font=("Consolas", 11, "bold"), fg=ACCENT_GREEN, bg="#161B22"
        )
        self.turn_label.pack(side="left", padx=10)

        self.moves_label = tk.Label(
            self.top_bar, text="Tentatives: 0", 
            font=("Consolas", 11, "bold"), fg=TEXT_COLOR, bg="#161B22"
        )
        self.moves_label.pack(side="left", padx=10)

        btn_save = tk.Button(
            self.top_bar, text="💾 Sauvegarder", 
            font=("Consolas", 9, "bold"), bg="#1F6FEB", fg="#FFFFFF", 
            bd=0, cursor="hand2", command=self.save_game, padx=8, pady=4
        )
        btn_save.pack(side="right", padx=4)

        btn_menu = tk.Button(
            self.top_bar, text="🏠 Menu", 
            font=("Consolas", 9, "bold"), bg="#30363D", fg=TEXT_COLOR, 
            bd=0, cursor="hand2", command=lambda: controller.show_frame(MainMenu), padx=8, pady=4
        )
        btn_menu.pack(side="right", padx=4)

        # Plateau de jeu
        self.grid_frame = tk.Frame(self, bg=BG_DARK)
        self.grid_frame.pack(expand=True)

        # Overlay pour les notifications de confinement
        self.notification_label = tk.Label(
            self,
            font=("Consolas", 16, "bold"),
            bd=3,
            relief="solid",
            padx=25,
            pady=12
        )
        self.notification_timer = None
        self.current_player = 1

        self.cards = []
        self.selected_cards = []

    def show_notification(self, text, bg_color, fg_color):
        """Affiche un message de statut SCP au centre de l'écran."""
        if self.notification_timer is not None:
            self.after_cancel(self.notification_timer)

        self.notification_label.config(
            text=text,
            bg=bg_color,
            fg=fg_color,
            highlightbackground=fg_color
        )
        self.notification_label.place(relx=0.5, rely=0.5, anchor="center")
        self.notification_label.lift()

        self.notification_timer = self.after(1400, self.notification_label.place_forget)

    def start_new_game(self):
        """Réinitialise et démarre une nouvelle session."""
        self.controller.score_p1 = 0
        self.controller.score_p2 = 0
        self.controller.moves = 0
        self.controller.matched_pairs = 0
        self.controller.is_animating = False
        self.current_player = 1
        self.update_labels()
        if self.notification_label.winfo_viewable():
            self.notification_label.place_forget()

        # Nettoyage complet
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.cards = []
        self.selected_cards = []

        # Génération des 15 paires d'anomalies SCP
        num_pairs = self.controller.total_pairs
        selected_emojis = EMOJIS[:num_pairs] * 2
        random.shuffle(selected_emojis)

        # Placement des 30 cartes
        for i, symbol in enumerate(selected_emojis):
            row = i // self.controller.grid_cols
            col = i % self.controller.grid_cols
            card = AnimatedCard(self.grid_frame, symbol, self.on_card_click)
            card.grid(row=row, column=col, padx=5, pady=5)
            self.cards.append(card)

    def on_card_click(self, card):
        """Gestion du clic utilisateur."""
        if self.controller.is_animating or card in self.selected_cards:
            return

        self.controller.is_animating = True
        self.selected_cards.append(card)
        card.animate_flip(show_symbol=True, callback=self.after_card_flip)

    def get_current_player_name(self):
        return self.controller.player1_name if self.current_player == 1 else self.controller.player2_name

    def after_card_flip(self):
        """Vérifie l'alignement des entités après retournement."""
        if len(self.selected_cards) < 2:
            self.controller.is_animating = False
            return

        self.controller.moves += 1
        card1, card2 = self.selected_cards
        curr_name = self.get_current_player_name()

        if card1.symbol == card2.symbol:
            # Confinement réussi (+1 score)
            if self.current_player == 1:
                self.controller.score_p1 += 1
            else:
                self.controller.score_p2 += 1

            # Mettre à jour immédiatement le tableau des deux joueurs
            self.controller.update_live_score(
                self.controller.player1_name, 
                self.controller.score_p1,
                self.controller.player2_name,
                self.controller.score_p2,
                self.controller.moves
            )

            card1.set_matched()
            card2.set_matched()
            self.selected_cards = []
            self.controller.matched_pairs += 1
            self.controller.is_animating = False

            # Notification de confinement
            self.show_notification(f"🔒 ANOMALIE CONFINÉE ! 🔒\nAgent {curr_name} gagne +1 point.\nConserve la main.", "#132338", "#2EA043")

            # Condition de fin de confinement
            if self.controller.matched_pairs == self.controller.total_pairs:
                if self.controller.score_p1 > self.controller.score_p2:
                    winner_msg = f"🏆 Victoire du Confinement : {self.controller.player1_name} !"
                elif self.controller.score_p2 > self.controller.score_p1:
                    winner_msg = f"🏆 Victoire du Confinement : {self.controller.player2_name} !"
                else:
                    winner_msg = "🤝 Équilibre parfait entre les agents !"

                messagebox.showinfo(
                    "🛡️ MISSION COMPLETE", 
                    f"{winner_msg}\n\n"
                    f"Score {self.controller.player1_name} : {self.controller.score_p1}\n"
                    f"Score {self.controller.player2_name} : {self.controller.score_p2}\n"
                    f"Tentatives totales : {self.controller.moves}"
                )
                self.controller.show_frame(MainMenu)
        else:
            # Changement d'agent
            next_player = 2 if self.current_player == 1 else 1
            self.current_player = next_player
            next_name = self.get_current_player_name()
            
            self.show_notification(f"⚠️ DISCORDANCE ANOMALE ⚠️\nTour passe à l'Agent : {next_name}", "#2D1517", "#FF6E6C")
            
            self.after(700, self.hide_selected_cards)

        self.update_labels()

    def hide_selected_cards(self):
        """Retourne les deux cartes non correspondantes."""
        if len(self.selected_cards) == 2:
            card1, card2 = self.selected_cards
            card1.animate_flip(show_symbol=False)
            card2.animate_flip(show_symbol=False, callback=self.reset_selection)
        else:
            self.reset_selection()

    def reset_selection(self):
        self.selected_cards = []
        self.controller.is_animating = False

    def update_labels(self):
        p1_name = self.controller.player1_name
        p2_name = self.controller.player2_name
        curr_name = self.get_current_player_name()

        self.score_p1_label.config(text=f"🔵 {p1_name}: {self.controller.score_p1}")
        self.score_p2_label.config(text=f"🟡 {p2_name}: {self.controller.score_p2}")
        self.turn_label.config(text=f"👉 Actif: {curr_name}")
        self.moves_label.config(text=f"Essais: {self.controller.moves}")

    def save_game(self):
        """Sauvegarde l'état de la mission sous un nom unique."""
        default_filename = f"session_{self.controller.player1_name}_vs_{self.controller.player2_name}_{int(time.time())}.json"
        filepath = os.path.join(SAVE_DIR, default_filename)

        game_state = {
            "player1_name": self.controller.player1_name,
            "player2_name": self.controller.player2_name,
            "score_p1": self.controller.score_p1,
            "score_p2": self.controller.score_p2,
            "current_player": self.current_player,
            "moves": self.controller.moves,
            "matched_pairs": self.controller.matched_pairs,
            "cards": [
                {
                    "symbol": card.symbol,
                    "is_flipped": card.is_flipped,
                    "is_matched": card.is_matched
                }
                for card in self.cards
            ]
        }
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(game_state, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Sauvegarde", "Données de la mission sauvegardées !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la sauvegarde : {e}")

    def load_game_data(self, filepath):
        """Restaure la session SCP depuis le fichier JSON spécifié."""
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.controller.player1_name = data.get("player1_name", "Agent Alpha")
            self.controller.player2_name = data.get("player2_name", "Agent Bravo")
            self.controller.score_p1 = data.get("score_p1", 0)
            self.controller.score_p2 = data.get("score_p2", 0)
            self.current_player = data.get("current_player", 1)
            self.controller.moves = data.get("moves", 0)
            self.controller.matched_pairs = data.get("matched_pairs", 0)
            self.controller.is_animating = False
            self.update_labels()

            for widget in self.grid_frame.winfo_children():
                widget.destroy()

            self.cards = []
            self.selected_cards = []

            for i, cdata in enumerate(data.get("cards", [])):
                row = i // self.controller.grid_cols
                col = i % self.controller.grid_cols
                card = AnimatedCard(self.grid_frame, cdata["symbol"], self.on_card_click)
                card.grid(row=row, column=col, padx=5, pady=5)

                if cdata.get("is_matched", False):
                    card.set_matched()
                    card.is_flipped = True
                    card.itemconfig(card.text, text=card.symbol)
                elif cdata.get("is_flipped", False):
                    card.is_flipped = True
                    card.itemconfig(card.rect, fill=BG_CARD_FRONT, outline=ACCENT_BLUE)
                    card.itemconfig(card.text, text=card.symbol)

                self.cards.append(card)
            return True
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de restaurer la mission : {e}")
            return False


class HighScoresScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller

        # Configuration responsive
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title = tk.Label(
            self, text="📊 ARCHIVES REGISTRE SCP (DUELS DE CONFINEMENT) 📊", 
            font=("Consolas", 20, "bold"), fg=ACCENT_RED, bg=BG_DARK
        )
        title.grid(row=0, column=0, pady=(25, 10))

        # Configuration du style sombre pour le Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview", 
            background="#161B22", 
            foreground=TEXT_COLOR, 
            fieldbackground="#161B22", 
            rowheight=35,
            font=("Consolas", 10)
        )
        style.configure(
            "Treeview.Heading", 
            background="#21262D", 
            foreground=ACCENT_BLUE, 
            font=("Consolas", 10, "bold")
        )
        style.map("Treeview", background=[("selected", "#1F6FEB")], foreground=[("selected", "#FFFFFF")])

        tree_frame = tk.Frame(self, bg=BG_DARK)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("rang", "p1", "p2", "total", "moves", "date")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        self.tree.heading("rang", text="Clearance")
        self.tree.heading("p1", text="Agent 1 (Score)")
        self.tree.heading("p2", text="Agent 2 (Score)")
        self.tree.heading("total", text="Total Paires")
        self.tree.heading("moves", text="Essais")
        self.tree.heading("date", text="Horodatage")

        self.tree.column("rang", width=90, anchor="center")
        self.tree.column("p1", width=180, anchor="center")
        self.tree.column("p2", width=180, anchor="center")
        self.tree.column("total", width=110, anchor="center")
        self.tree.column("moves", width=80, anchor="center")
        self.tree.column("date", width=130, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        btn_back = tk.Button(
            self, text="⬅️ RETOUR AU TERMINAL", 
            font=("Consolas", 11, "bold"), bg="#30363D", fg=TEXT_COLOR, 
            bd=0, width=24, height=2, cursor="hand2",
            command=lambda: controller.show_frame(MainMenu)
        )
        btn_back.grid(row=2, column=0, pady=20)

    def on_show(self):
        """Mise à jour des résultats enregistrés séparément par joueur."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Redéfinition des colonnes pour un affichage individuel
        self.tree["columns"] = ("rang", "player", "score", "moves", "date")
        self.tree.heading("rang", text="Clearance")
        self.tree.heading("player", text="Agent SCP")
        self.tree.heading("score", text="Paires Trouvées (Score)")
        self.tree.heading("moves", text="Essais Partie")
        self.tree.heading("date", text="Horodatage")

        self.tree.column("rang", width=100, anchor="center")
        self.tree.column("player", width=220, anchor="center")
        self.tree.column("score", width=180, anchor="center")
        self.tree.column("moves", width=110, anchor="center")
        self.tree.column("date", width=150, anchor="center")

        if os.path.exists(SCORES_FILE):
            try:
                with open(SCORES_FILE, "r", encoding="utf-8") as f:
                    scores = json.load(f)

                for idx, entry in enumerate(scores, 1):
                    rank_str = f"Level {idx}"
                    player_name = entry.get("player", entry.get("p1_name", "Inconnu"))
                    score_val = entry.get("score", entry.get("p1_score", 0))

                    self.tree.insert("", "end", values=(
                        rank_str, player_name, score_val, entry.get("moves", 0), entry.get("date", "-")
                    ))
            except Exception as e:
                print(f"Erreur chargement archives: {e}")


class SettingsMenu(tk.Frame):
    """Onglet Paramètres révisé : Plein Écran, gestionnaires multi-sauvegardes et interface responsive sans texte coupé."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title = tk.Label(
            self, text="⚙️ PARAMETRES DU SYSTEME SCP ⚙️", 
            font=("Consolas", 20, "bold"), fg=ACCENT_BLUE, bg=BG_DARK
        )
        title.grid(row=1, column=0, pady=(15, 15))

        # Box affichage & plein écran
        settings_box = tk.Frame(self, bg="#161B22", padx=20, pady=12, highlightbackground="#30363D", highlightthickness=1)
        settings_box.grid(row=2, column=0, pady=10, sticky="ew", padx=40)
        settings_box.columnconfigure(0, weight=1)

        self.fullscreen_var = tk.BooleanVar(value=False)
        chk_fullscreen = tk.Checkbutton(
            settings_box, 
            text=" 🖥️ Mode Plein Écran (Fullscreen)", 
            variable=self.fullscreen_var,
            font=("Consolas", 11, "bold"),
            fg=TEXT_COLOR, bg="#161B22",
            selectcolor=BG_DARK,
            activebackground="#161B22",
            activeforeground=ACCENT_BLUE,
            command=self.toggle_fullscreen
        )
        chk_fullscreen.pack(pady=4, anchor="w")

        info_label = tk.Label(
            settings_box,
            text="Astuce : Touche F11 pour basculer en Plein Écran.",
            font=("Consolas", 9, "italic"),
            fg="#8B949E", bg="#161B22", justify="left"
        )
        info_label.pack(pady=(0, 4), anchor="w")

        # Box gestion des données / sauvegardes multiples
        data_box = tk.Frame(self, bg="#161B22", padx=20, pady=12, highlightbackground="#30363D", highlightthickness=1)
        data_box.grid(row=3, column=0, pady=10, sticky="ew", padx=40)
        data_box.columnconfigure(0, weight=1)

        data_title = tk.Label(
            data_box, text="🗑️ GESTION DES SAUVEGARDES",
            font=("Consolas", 12, "bold"), fg=ACCENT_RED, bg="#161B22"
        )
        data_title.pack(pady=(0, 8))

        # Liste des sauvegardes dans un cadre scroolable ou combobox
        save_select_frame = tk.Frame(data_box, bg="#161B22")
        save_select_frame.pack(fill="x", pady=5)

        tk.Label(save_select_frame, text="Sauvegarde à supprimer :", font=("Consolas", 10), fg=TEXT_COLOR, bg="#161B22").pack(side="left", padx=(0, 5))

        self.saves_combo = ttk.Combobox(save_select_frame, state="readonly", font=("Consolas", 9), width=35)
        self.saves_combo.pack(side="left", fill="x", expand=True, padx=5)

        btn_style_danger = {
            "font": ("Consolas", 10, "bold"),
            "bd": 0,
            "cursor": "hand2",
            "pady": 6
        }

        self.btn_delete_save = tk.Button(
            data_box, text="❌ SUPPRIMER LA SAUVEGARDE SELECTIONNEE",
            bg="#DA3633", fg="#FFFFFF",
            command=self.delete_selected_save, **btn_style_danger
        )
        self.btn_delete_save.pack(fill="x", pady=5)

        btn_delete_scores = tk.Button(
            data_box, text="⚠️ REINITIALISER LES ARCHIVES SCORES",
            bg="#8E1515", fg="#FFFFFF",
            command=self.delete_scores_file, **btn_style_danger
        )
        btn_delete_scores.pack(fill="x", pady=5)

        btn_back = tk.Button(
            self, text="⬅️ RETOUR AU MENU", 
            font=("Consolas", 11, "bold"), bg="#30363D", fg=TEXT_COLOR, 
            bd=0, width=22, height=2, cursor="hand2",
            command=lambda: controller.show_frame(MainMenu)
        )
        btn_back.grid(row=4, column=0, pady=15)

        # Raccourci F11 global
        self.controller.bind("<F11>", lambda e: self.toggle_fullscreen_key())

    def on_show(self):
        """Recharge la liste des fichiers de sauvegardes disponibles."""
        saves = [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
        self.saves_combo["values"] = saves
        if saves:
            self.saves_combo.current(0)
            self.btn_delete_save.config(state="normal", bg="#DA3633")
        else:
            self.saves_combo.set("Aucune sauvegarde disponible")
            self.btn_delete_save.config(state="disabled", bg="#161B22")

    def delete_selected_save(self):
        """Supprime la sauvegarde sélectionnée dans la boîte déroulante."""
        selected_file = self.saves_combo.get()
        if not selected_file or selected_file == "Aucune sauvegarde disponible":
            return

        filepath = os.path.join(SAVE_DIR, selected_file)
        if os.path.exists(filepath):
            if messagebox.askyesno("Purge", f"Voulez-vous supprimer '{selected_file}' ?"):
                try:
                    os.remove(filepath)
                    messagebox.showinfo("Purge", "La sauvegarde a été supprimée.")
                    self.on_show()
                except Exception as e:
                    messagebox.showerror("Erreur", f"Échec de la suppression : {e}")

    def delete_scores_file(self):
        """Efface complètement les archives de scores."""
        if os.path.exists(SCORES_FILE):
            if messagebox.askyesno("Réinitialisation", "Voulez-vous effacer TOUS les registres de scores SCP ?"):
                try:
                    os.remove(SCORES_FILE)
                    messagebox.showinfo("Réinitialisation", "Les archives ont été effacées.")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Échec de l'effacement : {e}")

    def toggle_fullscreen(self):
        self.controller.toggle_fullscreen(self.fullscreen_var.get())

    def toggle_fullscreen_key(self):
        new_state = not self.controller.attributes("-fullscreen")
        self.fullscreen_var.set(new_state)
        self.controller.toggle_fullscreen(new_state)


if __name__ == "__main__":
    app = MemoryGameApp()
    app.mainloop()