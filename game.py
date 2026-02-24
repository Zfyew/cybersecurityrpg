# Cyber Security RPG
# v2: level system and progression logic

import os
import time

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class Player:
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.score = 0
        self.health = 100
        self.max_levels = 3

    def status(self):
        print(f"\n  Player:  {self.name}")
        print(f"  Level:   {self.level} / {self.max_levels}")
        print(f"  Score:   {self.score}")
        print(f"  Health:  {self.health}")

    def add_score(self, points):
        self.score += points
        print(f"\n  [+] {points} points added. Total: {self.score}")

    def take_damage(self, amount):
        self.health -= amount
        print(f"\n  [-] Took {amount} damage. Health: {self.health}")
        if self.health <= 0:
            print("\n  You ran out of health. Game over.\n")
            exit()

    def next_level(self):
        if self.level < self.max_levels:
            self.level += 1
            print(f"\n  [+] Level up! Now on level {self.level}.")
        else:
            print("\n  All levels complete.")

def intro():
    clear()
    print("=" * 50)
    print("        CYBER SECURITY RPG")
    print("=" * 50)
    print("""
  You are a security analyst. Systems are being
  breached. It's your job to investigate, contain
  and fight back.

  Every level is based on a real attack scenario.
  Think carefully. Wrong moves cost you health.
    """)
    print("=" * 50)

def level_select(player):
    print(f"\n  Select a level:\n")
    levels = [
        "Level 1 — Password Cracking",
        "Level 2 — Port Scanning",
        "Level 3 — Breach Investigation"
    ]
    for i, lvl in enumerate(levels):
        locked = "" if i + 1 <= player.level else "  [LOCKED]"
        print(f"  {i + 1}. {lvl}{locked}")

    print("\n  Q. Quit")
    choice = input("\n  Select: ").strip().lower()
    return choice

intro()
name = input("\n  Enter your name: ").strip()
player = Player(name)

print(f"\n  Welcome, {player.name}.\n")
time.sleep(1)

while True:
    clear()
    print("=" * 50)
    print("        CYBER SECURITY RPG")
    print("=" * 50)
    player.status()
    print()
    choice = level_select(player)

    if choice == "q":
        print("\n  Exiting. See you next time.\n")
        break
    elif choice == "1":
        print("\n  Loading Level 1...\n")
        time.sleep(1)
    elif choice == "2" and player.level >= 2:
        print("\n  Loading Level 2...\n")
        time.sleep(1)
    elif choice == "3" and player.level >= 3:
        print("\n  Loading Level 3...\n")
        time.sleep(1)
    else:
        print("\n  Level locked or invalid option.\n")
        time.sleep(1)