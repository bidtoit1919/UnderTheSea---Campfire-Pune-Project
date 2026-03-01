import pygame
import math
import random
import sys
import string

pygame.init()
pygame.mixer.init()

W, H = 1200, 800
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Under the Surface")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 24)

BLACK = (10, 20, 30)
WHITE = (220, 240, 255)
CYAN = (0, 200, 255)
MAGENTA = (100, 220, 255)
RED = (255, 100, 80)
GREEN = (80, 255, 150)

COLOR_PALETTE = [
    (0, 200, 255),
    (100, 220, 255),
    (80, 255, 150),
    (200, 150, 255),
    (150, 200, 255),
    (100, 150, 255),
]



class Bubble:
    def __init__(self):
        self.x = random.randint(0, W)
        self.y = random.randint(0, H)
        self.radius = random.uniform(2, 8)
        self.speed = random.uniform(0.3, 1.2)
        self.wobble = random.uniform(0, 2 * math.pi)
        self.wobble_speed = random.uniform(0.02, 0.05)
    
    def update(self):
        self.y -= self.speed
        self.wobble += self.wobble_speed
        self.x += math.sin(self.wobble) * 0.5
        
        if self.y < -20:
            self.y = H + 20
            self.x = random.randint(0, W)
    
    def draw(self, surface, offset_y):
        alpha = int(30)
        color = (100, 180, 220)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y + offset_y)), int(self.radius), 1)
        pygame.draw.circle(surface, (150, 200, 255), (int(self.x - self.radius // 2), int(self.y - self.radius // 2 + offset_y)), int(self.radius // 3))

class Particle:
    def __init__(self, x, y, color, is_bubble=False):
        self.x = x
        self.y = y
        self.vx = (random.random() - 0.5) * 12
        if is_bubble:
            self.vy = (random.random() - 0.5) * 6 - 8
            self.radius = random.uniform(2, 6)
        else:
            self.vy = (random.random() - 0.5) * 12 - 3
            self.radius = 3
        self.life = 1.0
        self.color = color
        self.is_bubble = is_bubble
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.is_bubble:
            self.vx *= 0.98
        self.life -= 0.03 if self.is_bubble else 0.04
    
    def draw(self, surface, offset_y):
        if self.life > 0:
            life_factor = self.life
            if self.is_bubble:

                color_with_alpha = tuple(int(c * 0.8 * life_factor) for c in self.color)
                pygame.draw.circle(surface, color_with_alpha, (int(self.x), int(self.y + offset_y)), int(self.radius))

                if self.life > 0.3:
                    shine_color = tuple(int(c * 0.3 * life_factor) for c in (255, 255, 255))
                    pygame.draw.circle(surface, shine_color, (int(self.x - self.radius // 3), int(self.y - self.radius // 3 + offset_y)), max(1, int(self.radius // 2)))
            else:

                color_with_alpha = tuple(int(c * life_factor) for c in self.color)
                pygame.draw.circle(surface, color_with_alpha, (int(self.x), int(self.y + offset_y)), 3)
                if self.life > 0.5:
                    glow = int(4 * life_factor)
                    pygame.draw.circle(surface, color_with_alpha, (int(self.x), int(self.y + offset_y)), glow, 1)

class Node:
    def __init__(self, x, y, radius=40, color_idx=0):
        self.x = x
        self.y = y
        self.radius = radius
        self.pulse = 0
        self.color_idx = color_idx % len(COLOR_PALETTE)
        self.super_hop_timer = 0
    
    def draw(self, surface, player_node, next_node, offset_y):
        is_current = self == player_node
        is_next = self == next_node
        
        if is_current:
            color = (220, 240, 255)
        elif is_next:
            color = (150, 220, 255)
        else:
            color = COLOR_PALETTE[self.color_idx]
        
        width = 5 if is_next else 4
        

        pygame.draw.circle(surface, (15, 25, 40), (int(self.x), int(self.y + offset_y)), 52)
        

        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            ax = self.x + math.cos(rad) * 55
            ay = self.y + math.sin(rad) * 55
            pygame.draw.line(surface, color, (int(self.x), int(self.y + offset_y)), (int(ax), int(ay + offset_y)), 2)
        

        pygame.draw.circle(surface, color, (int(self.x), int(self.y + offset_y)), 50, width)
        

        inner_glow = tuple(int(c * 0.4) for c in color)
        pygame.draw.circle(surface, inner_glow, (int(self.x), int(self.y + offset_y)), 45, 2)
        

        if self.super_hop_timer > 0:
            progress = 1 - (self.super_hop_timer / 30)
            explosion_radius = int(50 + progress * 120)
            explosion_color = tuple(int(c * (1 - progress * 0.7)) for c in (255, 200, 100))
            pygame.draw.circle(surface, explosion_color, (int(self.x), int(self.y + offset_y)), explosion_radius, max(1, int(5 * (1 - progress))))
            self.super_hop_timer -= 1

class Player:
    def __init__(self, start_node):
        self.x = start_node.x
        self.y = start_node.y
        self.angle = -math.pi / 2
        self.radius = 10
        self.orbit_radius = 50
        self.angular_speed = 0.05
        self.direction = 1
        self.is_jumping = False
        self.vx = 0
        self.vy = 0
        self.node = start_node
        self.trail = []
    
    def draw(self, surface, offset_y):

        px, py = int(self.x), int(self.y + offset_y)
        

        pygame.draw.circle(surface, (100, 200, 255), (px, py), self.radius)
        

        pygame.draw.circle(surface, (150, 220, 255), (px, py), self.radius, 2)
        

        eye_x = px + int(math.cos(self.angle) * (self.radius * 0.6))
        eye_y = py + int(math.sin(self.angle) * (self.radius * 0.6))
        pygame.draw.circle(surface, (220, 255, 255), (eye_x, eye_y), 3)
        pygame.draw.circle(surface, (0, 100, 150), (eye_x, eye_y), 1)
        

        tail_angle = self.angle + math.pi
        tail_x = px + int(math.cos(tail_angle) * (self.radius + 3))
        tail_y = py + int(math.sin(tail_angle) * (self.radius + 3))
        

        fin_size = 6
        fin1 = (tail_x + int(math.cos(tail_angle + 0.5) * fin_size),
                tail_y + int(math.sin(tail_angle + 0.5) * fin_size))
        fin2 = (tail_x + int(math.cos(tail_angle - 0.5) * fin_size),
                tail_y + int(math.sin(tail_angle - 0.5) * fin_size))
        pygame.draw.polygon(surface, (80, 200, 220), [
            (tail_x, tail_y),
            fin1,
            fin2
        ])
        

        if self.trail:
            points = [(int(t['x']), int(t['y'] + offset_y)) for t in self.trail if t['life'] > 0]
            if len(points) > 1:
                for i in range(len(points) - 1):
                    alpha = int(100 * (1 - i / len(points)))
                    color = (80 + alpha // 3, 150 + alpha // 4, 200 + alpha // 3)
                    pygame.draw.line(surface, color, points[i], points[i + 1], 2)

GAME_OVER_PUNS = [
    "LOST IN THE ABYSS",
    "DEPTH TOO DEEP",
    "CRUSHED BY PRESSURE",
    "SWALLOWED BY DARKNESS",
    "WENT TOO FAR DOWN",
    "THE DEEP CLAIMED YOU",
]


def main():
    state = -1
    screen_ready = False
    score = 0
    high_score = 0
    cam_y = 0
    shake = 0
    nodes = []
    particles = []
    ambient_bubbles = [Bubble() for _ in range(40)]
    super_hop_text_timer = 0
    super_hop_text = ""
    game_over_pun = random.choice(GAME_OVER_PUNS)
    
    def init_game():
        nonlocal state, score, cam_y, nodes, particles, shake, super_hop_text_timer
        state = 2
        score = 0
        cam_y = 0
        shake = 0
        nodes = []
        particles = []
        super_hop_text_timer = 0
        
        start_y = H // 2 + 200
        for i in range(5):
            nodes.append(Node(W // 2, start_y, color_idx=i))
            start_y -= 250
        
        player.node = nodes[0]
        player.x = player.node.x
        player.y = player.node.y
        player.angle = -math.pi / 2
        player.is_jumping = False
        player.trail = []
        player.angular_speed = 0.05
    
    player = Player(Node(W // 2, H // 2))

    
    running = True
    while running:
        clock.tick(60)
        

        if state == -1:
            state = 0
            screen_ready = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if screen_ready:
                    if state == 0:
                        state = 1
                    elif state == 1:
                        init_game()
                    elif state == 2 and not player.is_jumping:
                        player.is_jumping = True
                        player.vx = math.cos(player.angle + math.pi/2 * player.direction) * 16
                        player.vy = math.sin(player.angle + math.pi/2 * player.direction) * 16
                        for _ in range(10):
                            particles.append(Particle(player.x, player.y, (100, 200, 255), is_bubble=True))
            if event.type == pygame.MOUSEBUTTONDOWN:
                if screen_ready:
                    if state == 0:
                        state = 1
                    elif state == 1:
                        init_game()
                    elif state == 2 and not player.is_jumping:
                        player.is_jumping = True
                        player.vx = math.cos(player.angle + math.pi/2 * player.direction) * 16
                        player.vy = math.sin(player.angle + math.pi/2 * player.direction) * 16
                        for _ in range(10):
                            particles.append(Particle(player.x, player.y, (100, 200, 255), is_bubble=True))
        
        if shake > 0:
            shake *= 0.9
        
        if super_hop_text_timer > 0:
            super_hop_text_timer -= 1
        
        if state == 2:
            if not player.is_jumping:
                player.angle += player.angular_speed * player.direction
                player.x = player.node.x + math.cos(player.angle) * player.orbit_radius
                player.y = player.node.y + math.sin(player.angle) * player.orbit_radius
            else:
                player.x += player.vx
                player.y += player.vy
                
                current_idx = nodes.index(player.node)
                furthest_collision = None
                furthest_advance = 0
                
                for advance in range(1, len(nodes) - current_idx):
                    target = nodes[current_idx + advance]
                    dx = player.x - target.x
                    dy = player.y - target.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    if dist <= player.orbit_radius + player.radius:
                        furthest_collision = target
                        furthest_advance = advance
                
                if furthest_collision:
                    player.node = furthest_collision
                    player.is_jumping = False
                    skip = furthest_advance
                    score += skip
                    

                    if skip > 2:
                        furthest_collision.super_hop_timer = 30
                        super_hop_text = f"EPIC DIVE x{skip}!"
                        super_hop_text_timer = 120
                        print(f"EPIC DIVE x{skip}!")
                    elif skip > 1:
                        super_hop_text = "GREAT DIVE!"
                        super_hop_text_timer = 90
                        print("GREAT DIVE!")
                    
                    player.angular_speed = min(0.2, 0.05 + score * 0.005)
                    player.direction = 1 if random.random() > 0.5 else -1
                    player.angle = math.atan2(player.y - player.node.y, player.x - player.node.x)
                    shake = 10
                    furthest_collision.pulse = 1
                    

                    for _ in range(20):
                        particles.append(Particle(player.x, player.y, (100, 200, 255), is_bubble=True))
                    for _ in range(8):
                        particles.append(Particle(player.x, player.y, (150, 220, 255), is_bubble=False))
                    
                    last_node = nodes[-1]
                    nx = max(player.orbit_radius + 40, min(W - (player.orbit_radius + 40), last_node.x + (random.random() - 0.5) * 350))
                    new_color_idx = (last_node.color_idx + 1) % len(COLOR_PALETTE)
                    nodes.append(Node(nx, last_node.y - (220 + random.random() * 100), color_idx=new_color_idx))
                    
                    if len(nodes) > 10:
                        nodes.pop(0)
                
                if abs(player.x - player.node.x) > 1000 or abs(player.y - player.node.y) > 1000:
                    state = 3
                    if score > high_score:
                        high_score = score
        
        for p in particles:
            p.update()
        particles = [p for p in particles if p.life > 0]
        
        for bubble in ambient_bubbles:
            bubble.update()
        
        cam_y += ((H // 2 - player.y) - cam_y) * 0.1
        offset_y = int(cam_y)
        
        screen.fill(BLACK)
        

        for i in range(H):
            alpha = int(20 * (1 - (i / H)))
            depth_color = (5 - alpha // 10, 20 - alpha // 10, 30)
            pygame.draw.line(screen, depth_color, (0, i), (W, i))
        

        for bubble in ambient_bubbles:
            bubble.draw(screen, offset_y)
        
        for node in nodes:
            next_node = nodes[nodes.index(player.node) + 1] if nodes.index(player.node) + 1 < len(nodes) else None
            node.draw(screen, player.node, next_node, offset_y)
        
        for p in particles:
            p.draw(screen, offset_y)
        
        player.draw(screen, offset_y)
        

        score_text = font.render(str(score), True, (100, 200, 255))
        screen.blit(score_text, (30, 30))
        
        best_text = small_font.render(f"HIGH: {high_score}", True, (80, 150, 200))
        screen.blit(best_text, (30, 90))
        

        if super_hop_text_timer > 0 and state == 2:
            progress = super_hop_text_timer / 120.0
            alpha = int(255 * min(progress, 1 - (progress - 0.7) / 0.3)) if progress > 0.7 else 255
            scale = 1.5 if super_hop_text_timer > 100 else 1 + 0.5 * progress
            super_hop_font = pygame.font.Font(None, int(60 * scale))
            super_hop_rendered = super_hop_font.render(super_hop_text, True, (255, 200, 100))
            screen.blit(super_hop_rendered, (W // 2 - super_hop_rendered.get_width() // 2, H // 3))
        

        if state == 0:
            screen.fill(BLACK)
            

            for bubble in ambient_bubbles:
                bubble.draw(screen, offset_y)
            

            title_font = pygame.font.Font(None, 120)
            title = title_font.render("UNDER THE SURFACE", True, CYAN)
            

            container_width = title.get_width() + 80
            container_height = 250
            container_x = W // 2 - container_width // 2
            container_y = H // 2 - container_height // 2
            

            pulse_val = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 500)
            border_color = (int(0 * pulse_val), int(200 * pulse_val), int(255 * pulse_val))
            

            pygame.draw.rect(screen, (5, 15, 25), (container_x, container_y, container_width, container_height))
            pygame.draw.rect(screen, border_color, (container_x, container_y, container_width, container_height), 3)
            

            pygame.draw.line(screen, (50, 150, 200), (container_x + 5, container_y + 5), (container_x + container_width - 5, container_y + 5), 1)
            pygame.draw.line(screen, (30, 80, 120), (container_x + 5, container_y + container_height - 5), (container_x + container_width - 5, container_y + container_height - 5), 1)
            

            screen.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 100))
            

            ship_icon_y = H // 2 + 40
            pygame.draw.circle(screen, (100, 200, 255), (W // 2, ship_icon_y), 15)
            pygame.draw.polygon(screen, (100, 200, 255), [
                (W // 2 - 10, ship_icon_y - 5),
                (W // 2 + 10, ship_icon_y - 5),
                (W // 2 + 8, ship_icon_y + 8),
                (W // 2 - 8, ship_icon_y + 8)
            ])
            

            pulse_val = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 400)
            blue = (0, 150, 255)
            white = (220, 240, 255)
            prompt_color = tuple(int(blue[i] * (1 - pulse_val) + white[i] * pulse_val) for i in range(3))
            prompt = small_font.render("► CLICK OR PRESS SPACE ◄", True, prompt_color)
            screen.blit(prompt, (W // 2 - prompt.get_width() // 2, H - 120))
        
        elif state == 1:
            screen.fill(BLACK)
            

            for bubble in ambient_bubbles:
                bubble.draw(screen, offset_y)
            

            tut_title = font.render("HOW TO PLAY", True, CYAN)
            screen.blit(tut_title, (W // 2 - tut_title.get_width() // 2, 50))
            pygame.draw.line(screen, (50, 150, 200), (W // 2 - tut_title.get_width() // 2, 120), (W // 2 + tut_title.get_width() // 2, 120), 2)
            
            tutorial_lines = [
                ("ORBIT", "Around the ship wheels", (100, 200, 255), (150, 220, 255)),
                ("JUMP", "To the next wheel using SPACE or CLICK", (100, 200, 255), (150, 220, 255)),
                ("SCORE", "Based on wheels you travel through", (255, 200, 100), (255, 220, 150)),
                ("DANGER", "Miss and fall into the abyss!", (255, 100, 100), (255, 150, 150)),
                ("CHALLENGE", "Travel through as many wheels as you can!", (100, 255, 150), (150, 255, 180)),
            ]
            
            y_pos = 160
            for title, desc, color1, color2 in tutorial_lines:
                title_text = pygame.font.Font(None, 32).render(title, True, color1)
                desc_text = small_font.render(desc, True, color2)
                screen.blit(title_text, (150, y_pos))
                screen.blit(desc_text, (150, y_pos + 35))
                y_pos += 95
            

            pulse_val = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 400)
            blue = (0, 150, 255)
            white = (220, 240, 255)
            prompt_color = tuple(int(blue[i] * (1 - pulse_val) + white[i] * pulse_val) for i in range(3))
            prompt = small_font.render("► CLICK OR PRESS SPACE TO START ◄", True, prompt_color)
            screen.blit(prompt, (W // 2 - prompt.get_width() // 2, H - 80))
        
        elif state == 3:


            
            overlay = pygame.Surface((W, H))
            overlay.set_alpha(230)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            

            game_over_font = pygame.font.Font(None, 100)
            game_over = game_over_font.render(random.choice(GAME_OVER_PUNS), True, RED)
            screen.blit(game_over, (W // 2 - game_over.get_width() // 2, H // 2 - 150))
            

            score_box_width = 400
            score_box_height = 140
            score_box_x = W // 2 - score_box_width // 2
            score_box_y = H // 2 + 20
            
            pygame.draw.rect(screen, (15, 30, 50), (score_box_x, score_box_y, score_box_width, score_box_height))
            pygame.draw.rect(screen, (255, 100, 80), (score_box_x, score_box_y, score_box_width, score_box_height), 3)
            
            final_score = pygame.font.Font(None, 60).render(f"{score}", True, (100, 200, 255))
            wheels_text = small_font.render("WHEELS TRAVELED", True, (200, 230, 255))
            screen.blit(final_score, (W // 2 - final_score.get_width() // 2, score_box_y + 20))
            screen.blit(wheels_text, (W // 2 - wheels_text.get_width() // 2, score_box_y + 70))
            
            if score == high_score and score > 0:
                new_record = pygame.font.Font(None, 48).render("★ NEW RECORD! ★", True, (255, 200, 100))
                screen.blit(new_record, (W // 2 - new_record.get_width() // 2, H // 2 + 180))
            
            pygame.display.flip()
            pygame.time.wait(2000)
            state = 0
            screen_ready = True
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
