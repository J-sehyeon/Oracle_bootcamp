import pygame
import random


screen_width = 800
screen_height = 400


# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (83, 165, 81) # 공룡 색상
GRAY = (83, 83, 83)   # 장애물 색상


# 게임 설정 변수
GRAVITY = 0.8
JUMP_STRENGTH = -16
GAME_SPEED = 7


class Dino(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 공룡 크기 40x60
        self.image = pygame.Surface((40, 60))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = 300 # 바닥 위치
       
        self.vel_y = 0
        self.is_jumping = False


    def jump(self):
        # 바닥에 있을 때만 점프 가능
        if not self.is_jumping:
            self.vel_y = JUMP_STRENGTH
            self.is_jumping = True


    def update(self):
        # 중력 적용
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y


        # 바닥 충돌 처리
        if self.rect.bottom >= 350:
            self.rect.bottom = 350
            self.is_jumping = False
            self.vel_y = 0


class Cactus(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 선인장 크기 랜덤 (너비 30 높이 40~70)
        height = random.randint(40, 70)
        self.image = pygame.Surface((30, height))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.rect.x = screen_width + random.randint(0, 100)
        self.rect.bottom = 350 # 땅 위에 위치


    def update(self):
        # 왼쪽으로 이동
        self.rect.x -= GAME_SPEED
        # 화면 밖으로 나가면 삭제
        if self.rect.right < 0:
            self.kill()








pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()


dino = Dino()
all_sprites.add(dino)


score = 0
running = True
game_over = False


font = pygame.font.Font(None, 40)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
       
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_over:
                    dino.jump()
                else:
                    # 게임 오버 시 스페이스바로 재시작
                    game_over = False
                    score = 0
                    GAME_SPEED = 7
                    obstacles.empty()
                    all_sprites.empty()
                    dino = Dino()
                    all_sprites.add(dino)


    screen.fill(WHITE)
    pygame.draw.line(screen, BLACK, (0, 350), (screen_width, 350), 2)


    if not game_over:
        # 게임 진행 로직
       
        # 장애물 생성 (약 2퍼센트 확률)
        if random.randint(0, 100) < 2:
            cactus = Cactus()
            all_sprites.add(cactus)
            obstacles.add(cactus)


        all_sprites.update()
       
        # 충돌 체크
        if pygame.sprite.spritecollide(dino, obstacles, False):
            game_over = True
           
        # 점수 증가
        score += 1
       
        # 난이도 상승 (점수 500점마다 속도 증가)
        if score % 500 == 0:
            GAME_SPEED += 1


    else:
        # 게임 오버 화면
        msg = font.render("GAME OVER", True, BLACK)
        msg_rect = msg.get_rect(center=(screen_width//2, screen_height//2))
        screen.blit(msg, msg_rect)
       
        retry_msg = font.render("Press SPACE to Retry", True, BLACK)
        retry_rect = retry_msg.get_rect(center=(screen_width//2, screen_height//2 + 50))
        screen.blit(retry_msg, retry_rect)


    # 모든 스프라이트 그리기
    all_sprites.draw(screen)
   
    # 점수 표시
    score_text = font.render(f"Score {score}", True, BLACK)
    screen.blit(score_text, (10, 10))


    pygame.display.flip()
    clock.tick(60)


pygame.quit()
