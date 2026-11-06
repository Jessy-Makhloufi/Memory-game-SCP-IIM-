import tkinter as tk
from tkinter import messagebox, ttk
import random
import json
import os
import time

# Fichiers de sauvegarde
SAVE_FILE = "memory_save.json"
SCORES_FILE = "memory_scores.json"

# Palette de couleurs modernes (Catppuccin Mocha palette)
BG_DARK = "#1E1E2E"
BG_CARD_BACK = "#313244"
BG_CARD_FRONT = "#45475A"
TEXT_COLOR = "#CDD6F4"
ACCENT_BLUE = "#89B4FA"
ACCENT_GREEN = "#A6E3A1"
ACCENT_RED = "#F38BA8"
CARD_BORDER = "#585B70"

# Symboles / Emojis pour les cartes
EMOJIS = [
    "🚀", "🎨", "🎮", "🎵", "🍕", "🐱", "💎", "🌟", 
    "🔥", "🦄", "🌈", "🍦", "⚽", "🚗", "👑"
]

class MemoryGameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Memory Game - Édition Moderne (30 Cartes)")
        self.geometry("900x750")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)

        # Variables du jeu
        self.score = 0
        self.moves = 0
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
        for PageClass in (MainMenu, GameScreen, HighScoresScreen):
            frame = PageClass(parent=self.container, controller=self)
            self.frames[PageClass] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainMenu)

    def show_frame(self, page_class):
        """Affiche l'écran demandé."""
        frame = self.frames[page_class]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()

    def save_high_score(self, score, moves):
        """Sauvegarde le score dans l'historique local."""
        scores = []
        if os.path.exists(SCORES_FILE):
            try:
                with open(SCORES_FILE, "r", encoding="utf-8") as f:
                    scores = json.load(f)
            except Exception:
                scores = []

        scores.append({
            "score": score,
            "moves": moves,
            "date": time.strftime("%Y-%m-%d %H:%M")
        })

        # Trier par score (décroissant) puis par nombre de coups (croissant)
        scores = sorted(scores, key=lambda x: (-x["score"], x["moves"]))[:10]

        try:
            with open(SCORES_FILE, "w", encoding="utf-8") as f:
                json.dump(scores, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du score: {e}")


class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller

        # Titre principal
        title = tk.Label(
            self, text="🧠 MEMORY GAME 🧠", 
            font=("Helvetica", 32, "bold"), 
            fg=ACCENT_BLUE, bg=BG_DARK
        )
        title.pack(pady=(80, 10))

        subtitle = tk.Label(
            self, text="Testez et améliorez votre mémoire !", 
            font=("Helvetica", 14), 
            fg=TEXT_COLOR, bg=BG_DARK
        )
        subtitle.pack(pady=(0, 40))

        # Style des boutons
        btn_style = {
            "font": ("Helvetica", 14, "bold"),
            "width": 22,
            "height": 2,
            "bd": 0,
            "cursor": "hand2",
            "activebackground": ACCENT_BLUE,
            "activeforeground": BG_DARK
        }

        btn_new = tk.Button(
            self, text="🎮 Nouvelle Partie", 
            bg=ACCENT_BLUE, fg=BG_DARK, 
            command=self.start_new_game, **btn_style
        )
        btn_new.pack(pady=10)

        self.btn_load = tk.Button(
            self, text="📂 Continuer Partie", 
            bg=ACCENT_GREEN, fg=BG_DARK, 
            command=self.load_game, **btn_style
        )
        self.btn_load.pack(pady=10)

        btn_scores = tk.Button(
            self, text="🏆 Tableau des Scores", 
            bg=BG_CARD_FRONT, fg=TEXT_COLOR, 
            command=lambda: controller.show_frame(HighScoresScreen), **btn_style
        )
        btn_scores.pack(pady=10)

        btn_quit = tk.Button(
            self, text="❌ Quitter", 
            bg=ACCENT_RED, fg=BG_DARK, 
            command=controller.quit, **btn_style
        )
        btn_quit.pack(pady=10)

    def on_show(self):
        """Vérifie si une sauvegarde existe pour activer/désactiver le bouton Continuer."""
        if os.path.exists(SAVE_FILE):
            self.btn_load.config(state="normal", bg=ACCENT_GREEN)
        else:
            self.btn_load.config(state="disabled", bg="#585B70")

    def start_new_game(self):
        game_screen = self.controller.frames[GameScreen]
        game_screen.start_new_game()
        self.controller.show_frame(GameScreen)

    def load_game(self):
        game_screen = self.controller.frames[GameScreen]
        if game_screen.load_game_data():
            self.controller.show_frame(GameScreen)


class AnimatedCard(tk.Canvas):
    """Carte personnalisée avec animation de retournement (flip animation)."""
    def __init__(self, parent, symbol, on_click_callback, size=95):
        super().__init__(parent, width=size, height=size, bg=BG_DARK, highlightthickness=0)
        self.symbol = symbol
        self.on_click_callback = on_click_callback
        self.size = size
        self.is_flipped = False
        self.is_matched = False

        # Dessin initial du dos de la carte (format carré avec léger arrondissement)
        self.rect = self.create_rounded_rect(4, 4, size-4, size-4, radius=8, fill=BG_CARD_BACK, outline=CARD_BORDER, width=2)
        self.text = self.create_text(size//2, size//2, text="❓", font=("Helvetica", 24), fill=TEXT_COLOR)

        self.bind("<Button-1>", self.handle_click)

    def create_rounded_rect(self, x1, y1, x2, y2, radius=12, **kwargs):
        """Dessine un rectangle carré à coins légèrement arrondis."""
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius,
                  x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2,
                  x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def handle_click(self, event):
        if not self.is_flipped and not self.is_matched:
            self.on_click_callback(self)

    def animate_flip(self, show_symbol, callback=None):
        """Animation de réduction puis d'expansion horizontale tout en préservant l'aspect carré."""
        steps = 5
        delay = 15  # millisecondes par étape

        def shrink(step):
            if step >= 0:
                w = (self.size // 2) * (step / steps)
                self.coords(self.rect, self.get_contracted_coords(w))
                self.after(delay, lambda: shrink(step - 1))
            else:
                # Étape médiane : changer l'état visuel
                self.is_flipped = show_symbol
                if show_symbol:
                    self.itemconfig(self.rect, fill=BG_CARD_FRONT, outline=ACCENT_BLUE)
                    self.itemconfig(self.text, text=self.symbol)
                else:
                    self.itemconfig(self.rect, fill=BG_CARD_BACK, outline=CARD_BORDER)
                    self.itemconfig(self.text, text="❓")
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

    def get_contracted_coords(self, w):
        cx = self.size // 2
        x1 = max(4, cx - w)
        x2 = min(self.size - 4, cx + w)
        y1, y2 = 4, self.size - 4
        radius = min(8, int(w))
        return [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius,
                x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2,
                x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]

    def set_matched(self):
        """Marque la carte comme correctement devinée."""
        self.is_matched = True
        self.itemconfig(self.rect, fill=ACCENT_GREEN, outline=ACCENT_GREEN)


class GameScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller

        # Barre d'informations (Score & Coups)
        self.top_bar = tk.Frame(self, bg=BG_DARK)
        self.top_bar.pack(fill="x", pady=15, padx=20)

        self.score_label = tk.Label(
            self.top_bar, text="Score: 0", 
            font=("Helvetica", 16, "bold"), fg=ACCENT_GREEN, bg=BG_DARK
        )
        self.score_label.pack(side="left", padx=20)

        self.moves_label = tk.Label(
            self.top_bar, text="Coups: 0", 
            font=("Helvetica", 16, "bold"), fg=ACCENT_BLUE, bg=BG_DARK
        )
        self.moves_label.pack(side="left", padx=20)

        btn_save = tk.Button(
            self.top_bar, text="💾 Sauvegarder", 
            font=("Helvetica", 11, "bold"), bg=BG_CARD_FRONT, fg=TEXT_COLOR, 
            bd=0, cursor="hand2", command=self.save_game, padx=10, pady=5
        )
        btn_save.pack(side="right", padx=10)

        btn_menu = tk.Button(
            self.top_bar, text="🏠 Menu", 
            font=("Helvetica", 11, "bold"), bg=BG_CARD_FRONT, fg=TEXT_COLOR, 
            bd=0, cursor="hand2", command=lambda: controller.show_frame(MainMenu), padx=10, pady=5
        )
        btn_menu.pack(side="right", padx=10)

        # Plateau de jeu
        self.grid_frame = tk.Frame(self, bg=BG_DARK)
        self.grid_frame.pack(expand=True)

        # Label d'overlay pour les notifications (Reussite / Échec)
        self.notification_label = tk.Label(
            self,
            font=("Helvetica", 18, "bold"),
            bd=2,
            relief="ridge",
            padx=20,
            pady=10
        )
        self.notification_timer = None

        self.cards = []
        self.selected_cards = []

    def show_notification(self, text, bg_color, fg_color):
        """Affiche un message temporaire en premier plan."""
        if self.notification_timer is not None:
            self.after_cancel(self.notification_timer)

        self.notification_label.config(
            text=text,
            bg=bg_color,
            fg=fg_color,
            highlightbackground=fg_color
        )
        # Positionnement au premier plan au centre supérieur du plateau
        self.notification_label.place(relx=0.5, rely=0.15, anchor="center")
        self.notification_label.lift()

        # Masquer la notification après 1.2 seconde
        self.notification_timer = self.after(1200, self.notification_label.place_forget)

    def start_new_game(self):
        """Rénitialise et démarre une nouvelle partie."""
        self.controller.score = 0
        self.controller.moves = 0
        self.controller.matched_pairs = 0
        self.controller.is_animating = False
        self.update_labels()
        if self.notification_label.winfo_viewable():
            self.notification_label.place_forget()

        # Nettoyage complet
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.cards = []
        self.selected_cards = []

        # Génération des 15 paires d'emojis mélangés (30 cartes au total)
        num_pairs = self.controller.total_pairs
        selected_emojis = EMOJIS[:num_pairs] * 2
        random.shuffle(selected_emojis)

        # Placement des 30 cartes sur 5 lignes et 6 colonnes
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

    def after_card_flip(self):
        """Vérifie l'état après le retournement d'une carte."""
        if len(self.selected_cards) < 2:
            self.controller.is_animating = False
            return

        self.controller.moves += 1
        card1, card2 = self.selected_cards

        if card1.symbol == card2.symbol:
            # Paire trouvée (+1 au score)
            self.controller.score += 1
            card1.set_matched()
            card2.set_matched()
            self.selected_cards = []
            self.controller.matched_pairs += 1
            self.controller.is_animating = False

            # Notification de succès
            self.show_notification("✨ Bravo ! Paire trouvée (+1) 🎉", BG_CARD_FRONT, ACCENT_GREEN)

            # Condition de victoire
            if self.controller.matched_pairs == self.controller.total_pairs:
                self.controller.save_high_score(self.controller.score, self.controller.moves)
                messagebox.showinfo(
                    "Victoire !", 
                    f"Bravo, vous avez trouvé toutes les paires !\n\nScore final : {self.controller.score}\nCoups joués : {self.controller.moves}"
                )
                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)
                self.controller.show_frame(MainMenu)
        else:
            # Notification d'échec
            self.show_notification("❌ Dommage ! Ce n'est pas la bonne paire", BG_CARD_FRONT, ACCENT_RED)
            # Non correspondant : masquage après délai
            self.after(700, self.hide_selected_cards)

        self.update_labels()

    def hide_selected_cards(self):
        """Retourne les deux cartes incorrectes."""
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
        self.score_label.config(text=f"Score: {self.controller.score}")
        self.moves_label.config(text=f"Coups: {self.controller.moves}")

    def save_game(self):
        """Sauvegarde la partie courante."""
        game_state = {
            "score": self.controller.score,
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
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(game_state, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Sauvegarde", "Partie sauvegardée avec succès !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {e}")

    def load_game_data(self):
        """Restaure la partie depuis le fichier JSON."""
        if not os.path.exists(SAVE_FILE):
            return False

        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.controller.score = data.get("score", 0)
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
            messagebox.showerror("Erreur", f"Impossible de charger la sauvegarde : {e}")
            return False


class HighScoresScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller

        title = tk.Label(
            self, text="🏆 Meilleurs Scores", 
            font=("Helvetica", 24, "bold"), fg=ACCENT_BLUE, bg=BG_DARK
        )
        title.pack(pady=30)

        # Configuration du style pour le Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview", 
            background=BG_CARD_BACK, 
            foreground=TEXT_COLOR, 
            fieldbackground=BG_CARD_BACK, 
            rowheight=35,
            font=("Helvetica", 11)
        )
        style.configure(
            "Treeview.Heading", 
            background=BG_CARD_FRONT, 
            foreground=ACCENT_BLUE, 
            font=("Helvetica", 12, "bold")
        )
        style.map("Treeview", background=[("selected", ACCENT_BLUE)], foreground=[("selected", BG_DARK)])

        columns = ("rang", "score", "moves", "date")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)

        self.tree.heading("rang", text="Rang")
        self.tree.heading("score", text="Score (Paires)")
        self.tree.heading("moves", text="Coups joués")
        self.tree.heading("date", text="Date")

        self.tree.column("rang", width=80, anchor="center")
        self.tree.column("score", width=140, anchor="center")
        self.tree.column("moves", width=140, anchor="center")
        self.tree.column("date", width=200, anchor="center")

        self.tree.pack(pady=20, padx=50)

        btn_back = tk.Button(
            self, text="⬅️ Retour au Menu", 
            font=("Helvetica", 12, "bold"), bg=BG_CARD_FRONT, fg=TEXT_COLOR, 
            bd=0, width=20, height=2, cursor="hand2",
            command=lambda: controller.show_frame(MainMenu)
        )
        btn_back.pack(pady=20)

    def on_show(self):
        """Mise à jour des résultats enregistrés."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        if os.path.exists(SCORES_FILE):
            try:
                with open(SCORES_FILE, "r", encoding="utf-8") as f:
                    scores = json.load(f)

                for idx, entry in enumerate(scores, 1):
                    medal = "🥇 " if idx == 1 else "🥈 " if idx == 2 else "🥉 " if idx == 3 else f"{idx}. "
                    self.tree.insert("", "end", values=(medal, entry["score"], entry["moves"], entry["date"]))
            except Exception:
                pass


if __name__ == "__main__":
    app = MemoryGameApp()
    app.mainloop()