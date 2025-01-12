if __name__ == "__main__":
    exit()

import pygame as pg
from .assets import *

# Sprites
class CarpetGear(pg.sprite.Sprite):
    def __init__(self, x, y, radius):
        super().__init__()
        self.original_image = pg.transform.smoothscale(textures["gear"], (radius * 2, radius * 2))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.angle = 0

    def update(self, dt):
        self.angle -= 100 * dt
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Hammer(pg.sprite.Sprite):
    def __init__(self, x, y, length):
        super().__init__()
        self.original_image = pg.transform.smoothscale(textures["hammer"], (length, length))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y - Nail.length // 2))
        self.offset = pg.Vector2(0, -length // 2)
        self.pos = pg.Vector2(x, y)
        self.collide_pos = self.pos + pg.Vector2(-190, -10)
        self.collide_rect = pg.Rect(self.collide_pos, (15, 20))
        self.angle = 0
        self.hitting = False 
        self.length = length
        self.rotate()

    def hit(self):
        self.dir = 1
        self.hitting = True

    def update(self, dt):
        if self.hitting:
            # Rotate counter clock-wise for 30° then the same in clock-wise
            if abs(self.angle) >= 30: self.dir = -1

            self.angle += 1000 * dt * self.dir
            self.rotate()

            if self.angle <= 0 and self.dir == -1: self.hitting = False

    # Rotate the hammer where the pivot is the bottom of the handle
    def rotate(self):
        rotated_image = pg.transform.rotate(self.original_image, self.angle + 45)
        rotated_offset = self.offset.rotate(-self.angle - 45)
        self.image = rotated_image
        self.rect = self.image.get_rect(center=self.pos + rotated_offset)

class Nail(pg.sprite.Sprite):
    length = 40
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.transform.smoothscale(textures["nail"], (0.37 * Nail.length, Nail.length))
        self.rect = self.image.get_rect(center=(x, y - Nail.length // 2))
        self.hit = False


class WoodPlanck(pg.sprite.Sprite):
    width = 250
    height = 30
    speed = 100
    period = SCREEN_WIDTH / speed + 1
    nail_spawn = pg.Vector2(width - 70, SCREEN_HEIGHT // 2 - 25 - 30)
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface((WoodPlanck.width, WoodPlanck.height))
        self.image.fill(0)
        self.rect = self.image.get_rect(center=(x + WoodPlanck.width // 2, y - WoodPlanck.height // 2))
        self.nailed = False
        self.timer = 0

        self.nail_group = pg.sprite.Group()

    def update(self, dt):
        self.timer += dt
        # Move the plank to the right
        dx = dt * WoodPlanck.speed
        self.rect.x += dx
        for nail in self.nail_group:
            nail.rect.x += dx

        # Kill the plank and nails when exiting the screen
        if self.rect.x >= SCREEN_WIDTH:
            self.kill()
            del self

    def draw(self, surface):
        self.nail_group.draw(surface)
        surface.blit(self.image, self.rect.topleft)

    def put_nail(self):
        # If the plank reach the spawn point, it allow to plant a nail and play a sound
        if self.rect.x < self.nail_spawn.x and self.rect.x + self.rect.width > self.nail_spawn.x:
            self.nail_group.add(Nail(self.nail_spawn.x, self.nail_spawn.y))
            sounds["nail"].play()

class Button(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, texture_name):
        super().__init__()
        self.image = pg.transform.smoothscale(textures[texture_name], (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# Objects
import csv
from datetime import datetime
class Player:
    def __init__(self, name = ''):
        self.name = name.lower()
        self.total_nails = 0
        self.hit = 0
        self.missed_inarow = 0
        self.hammed_inarow = 0
        self.life = 3
        self.file_path = SCOREBOARDS_DIR + self.name.strip() + ".csv"

        # Party Stats
        self.accuracy = 0.0
        self.missed = 0
        self.hammed = 0
        self.time = 0.0

        # Read user best score from log (if it exists)
        try:
            with open(self.file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['party'] == "best":
                        self.best_score = float(row['score'])
                        break
        except:
            self.best_score = 0

    def update(self, dt):
        self.time += dt;

        # Life
        if self.missed_inarow >= 3:
            self.life -= 1
            self.missed_inarow -= 3
        if self.hammed_inarow >= 6:
            self.life += 1
            self.hammed_inarow -= 6
            self.missed_inarow = 0

        # Clip life
        if self.life < 0:
            self.life = 0
        elif self.life > 3:
            self.life = 3

    def save(self):
        if len(self.name) <= 0: return

        from pathlib import Path

        party = list(self.get_stats().values())
        # Open player file
        if not Path(self.file_path).exists():
            # If file does not exist, create one
            with open(self.file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['party', 'score', 'accuracy', 'total_nails', 'missed', 'time', 'date'])
                writer.writerow(['best', 0.0, 0.0, 0, 0, 0.0, ''])

        player_log = []
        with open(self.file_path, 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                player_log.append(row)

        # If current score is higher than the best score, update the best party with the current one
        if self.score > self.best_score:
            player_log[1] = ['best'] + party

        # Find the occurence of the current party by counting the number of party already in the file and append the new party
        party_nb = len(player_log) - 2
        player_log.append([f"party_{party_nb}"] + party
                          )

        with open(self.file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(player_log)

    def calculate_stats(self):
        last_missed = self.missed
        self.missed = self.total_nails - self.hammed
        self.missed_inarow += self.missed - last_missed
        if self.missed + self.hit + self.hammed != 0:
            self.accuracy = round(self.hammed / (self.missed + self.hit + self.hammed) * 100.0, 1)
        # Score is based on the playing time and the accuracy
        self.score = round(self.time * self.accuracy / 50.0, 1)

    def get_stats(self):
        self.calculate_stats()
        data = {
                "score": self.score,
                "accuracy": self.accuracy,
                "total_nails": self.total_nails,
                "missed": self.missed,
                "time": round(self.time, 2),
                "date": datetime.now().strftime('%d %b %Y %H:%M:%S')
                }
        return data

class NailSequence():
    duration = WoodPlanck.width / WoodPlanck.speed - 0.5

    def __init__(self):
        self.plank : WoodPlanck
        self.count = -1
        self.running = False 
        # A sequence of nails is described by the normalized delay between two nails planting
        # The real delay is then compute with : sequence[i] * duration / len(sequence)
        self.sequences = [
                [1, 1, 1, 1, 1, 1, 1],
                [1, 0.5, 1, 0.5, 1, 0.5, 1, 0.5],

                # Generated with ChatGPT
                [1, 0.25, 1, 0.75, 1, 0.5],  # A simple variation with a mix of 1, 0.25, and 0.75
                [1, 1, 0.5, 0.5, 1, 1, 0.5, 0.5],  # Slightly more complex rhythm
                [1, 0.75, 1, 0.5, 1, 0.25, 1, 0.5],  # Varying intervals of 1, 0.5, and 0.25
                [0.5, 1, 0.5, 1, 0.5, 1, 0.5, 1],  # Alternating 0.5 and 1
                [1, 1, 0.5, 0.75, 0.5, 1, 1, 0.75],  # Complex rhythmic sequence

                [1, 0.5, 1, 0.5, 1],  # A shorter, simpler alternating rhythm
                [1, 0.5, 1, 0.75, 1, 0.25, 1],  # A rhythm that adds 0.75 and 0.25
                [1, 0.75, 0.5, 1, 0.25, 1],  # A mix of 0.5, 0.25, and 1
                [1, 1, 0.25, 1, 0.75, 1, 0.5],  # Mixing smaller intervals with larger ones

                [1, 0.5, 1, 0.75, 1, 0.25, 0.5],  # Increased complexity with 0.25, 0.5, and 0.75
                [1, 1, 0.25, 0.5, 1, 0.75, 1, 0.25],  # Mixing different rhythmic intervals
                [0.5, 1, 0.75, 1, 0.25, 0.5],  # Alternating between more complex intervals
                [1, 0.75, 0.25, 1, 0.5, 1],  # Adding a little more rhythm complexity

                [1],

                [1, 0.5, 1, 0.75, 1, 0.25, 0.5, 1, 1, 0.25, 0.75],  # Complex pattern with alternating intervals
                [1, 1, 0.5, 0.25, 1, 0.75, 1, 0.5, 1, 0.25, 0.75, 1],  # A very challenging pattern with varied intervals
                [1, 0.25, 0.75, 1, 0.5, 1, 0.5, 1, 0.25, 1, 0.75, 0.5],  # Longest and most complex sequence yet
                [1, 1, 0.25, 0.5, 1, 0.75, 0.5, 1, 0.25, 1, 0.75, 1, 0.5],  # Lengthy sequence with many shifts
                [1, 0.5, 0.75, 1, 0.25, 1, 0.75, 0.5, 1, 0.25, 1, 1, 0.75, 0.5],  # One of the longest sequences
                [1, 1, 0.5, 0.25, 1, 0.75, 0.25, 1, 0.5, 1, 1, 0.75, 1, 0.25, 0.5],  # Maximum complexity sequence with variable lengths
                [1, 0.75, 1, 0.5, 0.5, 1, 0.25, 1, 0.75, 0.5, 1, 1, 0.25, 1, 0.75, 0.5],  # High difficulty with longer sequence and many rhythm variations
                [1, 0.5, 1, 0.25, 0.5, 1, 1, 0.75, 1, 0.25, 1, 0.75, 0.5, 1, 1, 0.25, 1],

                [1, 0.25, 1, 0.5, 1, 0.75, 1, 0.25],  # Increasing rhythmic variation
                [1, 1, 0.5, 1, 0.25, 0.75, 1, 0.5],  # Longer, alternating rhythm with small intervals
                [1, 0.5, 1, 0.75, 1, 0.25, 1, 0.5, 0.75],  # A long, complex sequence with alternating intervals
                [1, 0.25, 0.5, 1, 0.75, 0.25, 1, 1, 0.5],  # A long, intricate pattern of rhythm changes

                [1, 0.5, 1, 0.25, 1, 0.75, 1, 0.5],  # More intricate rhythm
                [1, 1, 0.5, 1, 0.75, 0.25, 0.5, 1, 0.75],  # Increasing difficulty with alternating timing
                [1, 0.25, 1, 0.5, 1, 0.75, 0.5, 1, 0.25],  # A complex sequence with rhythm intervals
                [1, 1, 0.5, 0.25, 1, 0.75, 1, 0.5, 1, 0.25],  # A difficult sequence with multiple intervals

                [1] * 20  # Maximum length with the simplest rhythm (very long)
                ]

    def set_plank(self, plank):
        self.plank = plank

    def next(self):
        # Go to the next sequence
        self.timer = 0
        self.note_count = 0
        self.last_time = 0
        self.count += 1
        if self.count > len(self.sequences) - 1: self.count = 0
        self.running = True

    def update(self, dt):
        if self.count < 0: 
            return

        # End of a sequence
        if self.note_count > len(self.sequences[self.count]):
            self.running = False
            self.plank.nailed = True

        if self.running:
            # Iterate through the sequence and calculate the next time to put iterate
            next_time = self.last_time + self.sequences[self.count][self.note_count - 1] * (self.duration / sum(self.sequences[self.count]))
            if  self.timer == 0 or self.timer > next_time:
                self.last_time = self.timer
                self.plank.put_nail()
                self.note_count += 1

            # Increments timer to keep track of current sequence time
            self.timer += dt
