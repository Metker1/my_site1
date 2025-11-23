import pygame
import math
import random
import sys
import os
from pygame import gfxdraw


class SpriteManager:
    def __init__(self):
        self.soldier_sprites = {}
        self.create_sprites()

    def create_sprites(self):
        # Создаем простые пиксельные спрайты солдат
        self.create_soldier_sprites()

    def create_soldier_sprites(self):
        # Красный солдат - разные направления
        red_soldier = self.create_soldier_sprite((255, 0, 0), (255, 200, 150))
        blue_soldier = self.create_soldier_sprite((0, 0, 255), (200, 200, 255))

        # Создаем анимации для разных направлений
        for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
            self.soldier_sprites[f'red_{angle}'] = self.rotate_sprite(red_soldier, angle)
            self.soldier_sprites[f'blue_{angle}'] = self.rotate_sprite(blue_soldier, angle)

        # Спрайт мертвого солдата
        self.soldier_sprites['dead'] = self.create_dead_sprite()

    def create_soldier_sprite(self, uniform_color, skin_color):
        """Создает спрайт солдата 16x16 пикселей"""
        sprite = pygame.Surface((16, 16), pygame.SRCALPHA)

        # Тело (форма человека)
        pygame.draw.rect(sprite, uniform_color, (4, 8, 8, 8))  # Тело
        pygame.draw.rect(sprite, skin_color, (6, 4, 4, 4))  # Голова
        pygame.draw.rect(sprite, uniform_color, (2, 8, 2, 6))  # Левая рука
        pygame.draw.rect(sprite, uniform_color, (12, 8, 2, 6))  # Правая рука
        pygame.draw.rect(sprite, (50, 50, 50), (5, 12, 2, 4))  # Левая нога
        pygame.draw.rect(sprite, (50, 50, 50), (9, 12, 2, 4))  # Правая нога

        # Оружие (винтовка)
        pygame.draw.rect(sprite, (100, 100, 100), (8, 6, 6, 2))

        return sprite

    def create_dead_sprite(self):
        """Создает спрайт мертвого солдата"""
        sprite = pygame.Surface((16, 16), pygame.SRCALPHA)

        # Лежащее тело
        pygame.draw.rect(sprite, (100, 100, 100), (4, 8, 8, 4))
        pygame.draw.rect(sprite, (150, 150, 150), (6, 6, 4, 2))

        return sprite

    def rotate_sprite(self, sprite, angle):
        """Поворачивает спрайт на заданный угол"""
        return pygame.transform.rotate(sprite, angle)

    def get_soldier_sprite(self, team, angle, state='alive'):
        """Возвращает спрайт солдата для заданной команды и направления"""
        if state == 'dead':
            return self.soldier_sprites['dead']

        angle_key = round(angle / 45) * 45  # Округляем до ближайших 45 градусов
        return self.soldier_sprites[f'{team}_{angle_key}']


class Soldier:
    def __init__(self, x, y, team, soldier_id):
        self.x = x
        self.y = y
        self.team = team  # 'red' или 'blue'
        self.id = soldier_id
        self.health = 100
        self.speed = random.uniform(1.0, 2.0)
        self.reload_time = 0
        self.target = None
        self.state = 'moving'  # moving, shooting, dead
        self.angle = 0
        self.size = 16

    def update(self, enemies, dt, bullets):
        if self.state == 'dead':
            return

        self.reload_time = max(0, self.reload_time - dt)

        # Поиск цели
        if not self.target or self.target.state == 'dead':
            self.find_target(enemies)

        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            self.angle = math.degrees(math.atan2(-dy, dx))  # Угол для спрайта

            if distance < 150:  # Дистанция стрельбы
                self.state = 'shooting'

                if self.reload_time <= 0:
                    self.shoot(math.atan2(dy, dx), bullets)
                    self.reload_time = 1.0  # Перезарядка 1 секунда
            else:
                self.state = 'moving'
                # Движение к цели
                if distance > 0:
                    self.x += (dx / distance) * self.speed
                    self.y += (dy / distance) * self.speed
        else:
            self.state = 'moving'
            # Случайное блуждание
            self.angle = random.uniform(0, 360)
            self.x += math.cos(math.radians(self.angle)) * self.speed
            self.y += math.sin(math.radians(self.angle)) * self.speed

        # Границы поля боя
        self.x = max(50, min(1150, self.x))
        self.y = max(50, min(750, self.y))

    def find_target(self, enemies):
        closest = None
        min_dist = float('inf')

        for enemy in enemies:
            if enemy.team != self.team and enemy.state != 'dead':
                dist = math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    closest = enemy

        self.target = closest

    def shoot(self, angle, bullets):
        bullet_speed = 5
        bullets.append(Bullet(
            self.x, self.y,
            math.cos(angle) * bullet_speed,
            math.sin(angle) * bullet_speed,
            self.team
        ))

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.state = 'dead'
            return True
        return False

    def draw(self, screen, sprite_manager):
        if self.state == 'dead':
            sprite = sprite_manager.get_soldier_sprite(self.team, self.angle, 'dead')
        else:
            sprite = sprite_manager.get_soldier_sprite(self.team, self.angle)

        # Рисуем спрайт
        screen.blit(sprite, (int(self.x - 8), int(self.y - 8)))

        # Полоска здоровья
        if self.state != 'dead':
            health_width = 20
            health_height = 4
            health_x = self.x - health_width // 2
            health_y = self.y - 15

            # Фон полоски
            pygame.draw.rect(screen, (50, 50, 50),
                             (health_x, health_y, health_width, health_height))

            # Здоровье
            health_color = (0, 255, 0) if self.health > 50 else (255, 255, 0) if self.health > 25 else (255, 0, 0)
            pygame.draw.rect(screen, health_color,
                             (health_x, health_y, health_width * (self.health / 100), health_height))


class Bullet:
    def __init__(self, x, y, vx, vy, team):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.team = team
        self.color = (255, 255, 0)
        self.size = 3
        self.lifetime = 3.0

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= dt

    def is_alive(self):
        return self.lifetime > 0 and 0 < self.x < 1200 and 0 < self.y < 800

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)


class Explosion:
    def __init__(self, x, y, power=1.0):
        self.x = x
        self.y = y
        self.particles = []
        self.duration = 0.8
        self.timer = self.duration
        self.power = power

        # Создаем частицы взрыва
        for _ in range(int(30 * power)):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8) * power
            life = random.uniform(0.3, 1.0)
            size = random.uniform(2, 6) * power

            self.particles.append({
                'x': x, 'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': life,
                'max_life': life,
                'size': size,
                'color': random.choice([(255, 100, 0), (255, 255, 0), (255, 50, 0)])
            })

    def update(self, dt):
        self.timer -= dt
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2
            particle['life'] -= dt

    def is_alive(self):
        return self.timer > 0

    def draw(self, screen):
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / particle['max_life']))
                size = particle['size'] * (particle['life'] / particle['max_life'])
                color = particle['color']

                pygame.draw.circle(screen, color,
                                   (int(particle['x']), int(particle['y'])),
                                   max(1, int(size)))


class BattleSimulation:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1200, 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("⚔️ Battle Simulation with Sprites - R: Reset, SPACE: Pause")

        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False

        # Менеджер спрайтов
        self.sprite_manager = SpriteManager()

        # Игровые объекты
        self.red_team = []
        self.blue_team = []
        self.bullets = []
        self.explosions = []

        self.setup_armies()

        # Статистика
        self.red_kills = 0
        self.blue_kills = 0
        self.battle_time = 0

    def setup_armies(self):
        # Красная армия (слева)
        for i in range(20):
            self.red_team.append(Soldier(
                random.uniform(100, 400),
                random.uniform(100, 700),
                'red', i
            ))

        # Синяя армия (справа)
        for i in range(20):
            self.blue_team.append(Soldier(
                random.uniform(800, 1100),
                random.uniform(100, 700),
                'blue', i
            ))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.reset_simulation()
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_1:
                    x = random.uniform(200, 1000)
                    y = random.uniform(200, 600)
                    self.explosions.append(Explosion(x, y, 2.0))

    def reset_simulation(self):
        self.red_team.clear()
        self.blue_team.clear()
        self.bullets.clear()
        self.explosions.clear()
        self.setup_armies()
        self.red_kills = 0
        self.blue_kills = 0
        self.battle_time = 0

    def update(self, dt):
        if self.paused:
            return

        self.battle_time += dt

        # Обновление солдат
        all_soldiers = self.red_team + self.blue_team
        alive_red = [s for s in self.red_team if s.state != 'dead']
        alive_blue = [s for s in self.blue_team if s.state != 'dead']

        for soldier in all_soldiers:
            enemies = alive_blue if soldier.team == 'red' else alive_red
            soldier.update(enemies, dt, self.bullets)

        # Обновление пуль
        for bullet in self.bullets[:]:
            bullet.update(dt)

            if not bullet.is_alive():
                self.bullets.remove(bullet)
                continue

            # Проверка попаданий
            targets = alive_blue if bullet.team == 'red' else alive_red
            for target in targets[:]:
                distance = math.sqrt((bullet.x - target.x) ** 2 + (bullet.y - target.y) ** 2)
                if distance < target.size:
                    if target.take_damage(25):
                        if bullet.team == 'red':
                            self.red_kills += 1
                        else:
                            self.blue_kills += 1
                        self.explosions.append(Explosion(target.x, target.y, 0.7))
                    self.bullets.remove(bullet)
                    break

        # Обновление взрывов
        for explosion in self.explosions[:]:
            explosion.update(dt)
            if not explosion.is_alive():
                self.explosions.remove(explosion)

    def draw_terrain(self):
        # Фон поля боя
        self.screen.fill((30, 60, 30))

        # Трава с текстурой
        for x in range(0, self.width, 20):
            for y in range(0, self.height, 20):
                shade = random.randint(20, 40)
                pygame.draw.rect(self.screen, (30 + shade, 60 + shade, 30 + shade),
                                 (x, y, 20, 20), 1)

        # Линия фронта
        pygame.draw.line(self.screen, (100, 100, 100), (self.width // 2, 0), (self.width // 2, self.height), 2)

    def draw_ui(self):
        font = pygame.font.Font(None, 36)

        # Статистика
        red_alive = len([s for s in self.red_team if s.state != 'dead'])
        blue_alive = len([s for s in self.blue_team if s.state != 'dead'])

        red_text = font.render(f"Red: {red_alive} | Kills: {self.red_kills}", True, (255, 0, 0))
        blue_text = font.render(f"Blue: {blue_alive} | Kills: {self.blue_kills}", True, (0, 0, 255))

        self.screen.blit(red_text, (20, 20))
        self.screen.blit(blue_text, (self.width - 250, 20))

        time_text = font.render(f"Time: {int(self.battle_time)}s", True, (255, 255, 255))
        self.screen.blit(time_text, (self.width // 2 - 60, 20))

        # Победа
        if red_alive == 0 and blue_alive > 0:
            win_text = font.render("BLUE TEAM WINS!", True, (0, 0, 255))
            self.screen.blit(win_text, (self.width // 2 - 100, self.height // 2))
        elif blue_alive == 0 and red_alive > 0:
            win_text = font.render("RED TEAM WINS!", True, (255, 0, 0))
            self.screen.blit(win_text, (self.width // 2 - 100, self.height // 2))

    def render(self):
        self.draw_terrain()

        # Рисуем взрывы
        for explosion in self.explosions:
            explosion.draw(self.screen)

        # Рисуем пули
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # Рисуем солдат со спрайтами
        for soldier in self.red_team + self.blue_team:
            soldier.draw(self.screen, self.sprite_manager)

        self.draw_ui()
        pygame.display.flip()

    def run(self):
        print("⚔️ Battle Simulation with Sprites Started!")
        print("Controls: R-Reset, SPACE-Pause, 1-Explosion, ESC-Exit")

        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    battle = BattleSimulation()
    battle.run()