# Cyber Security RPG
# v1: basic game engine and player class

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

    def status(self):
        print(f"\n  Player:  {self.name}")
        print(f"  Level:   {self.level}")
        print(f"  Score:   {self.score}")
        print(f"  Health:  {self.health}")

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

intro()
name = input("\n  Enter your name: ").strip()
player = Player(name)

print(f"\n  Welcome, {player.name}. Let's see what you've got.\n")
time.sleep(1)
player.status()
print()