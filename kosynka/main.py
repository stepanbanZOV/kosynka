import pygame  # Импортируем библиотеку Pygame для создания игры
import sys  # Импортируем модуль sys для завершения программы
import os  # Импортируем модуль os для работы с путями к файлам
import random  # Импортируем модуль random для случайного перемешивания карт

pygame.init()  # Инициализация Pygame
# Параметры окна
size = width, height = 960, 720  # Размеры окна игры
screen = pygame.display.set_mode(size)  # Создаем окно игры с заданными размерами
backgr=pygame.image.load("assets/background.png")
screen.blit(backgr,(0,0))  # Загрузка фона
pygame.display.set_caption("Pasjans Kosynka")  # Устанавливаем заголовок окна
pygame.mixer.music.load("Pasjans-Kosynka-OST-Chill.mp3")  # Загрузка музыки
pygame.mixer.music.play(-1)  # Зацикленное проигрывание музыки
pygame.time.Clock().tick(30)  # Ограничение на 30 кадров в секунду для экономии заряда

# Загрузка изображений карт
card_images = {}  # Словарь для хранения изображений карт
suits = ['hearts', 'diamonds', 'clubs', 'spades']  # Масти карт
values = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']  # Значения карт
for suit in suits:  # Для каждой масти
    for value in values:  # Для каждого значения
        card_name = f"{value}_of_{suit}"  # Имя файла с изображением карты
        image_path = os.path.join('assets', 'cards', f"{card_name}.png")  # Путь к файлу изображения
        card_images[card_name] = pygame.image.load(image_path)  # Загрузка изображения карты в словарь
back_image = pygame.image.load(os.path.join('assets', 'cards', 'back.png'))  # Загружаем изображение обратной стороны карты

# Класс для представления карты
class Card:
    def __init__(self, name, image, value, suit, color):
        self.name = name  # Имя карты (например, "ace_of_spades")
        self.image = image  # Изображение карты
        self.value = value  # Значение карты (1 для туза, 11 для валета и т.д.)
        self.suit = suit  # Масть карты
        self.color = color  # Цвет карты (красный или черный)
        self.face_up = False  # Лицевая сторона карты вверх (по умолчанию - нет)
    def draw(self, screen, pos):
        # Рисуем карту лицевой стороной вверх или обратной стороной, в зависимости от состояния face_up
        screen.blit(self.image if self.face_up else back_image, pos)

# Класс для представления столбца карт
class Column:
    def __init__(self):
        self.cards = []  # Список карт в столбце
    def add_card(self, card):
        self.cards.append(card)  # Добавляем карту в столбец
    def remove_cards(self, start_idx):
        removed_cards = self.cards[start_idx:]  # Удаляем карты, начиная с указанного индекса
        self.cards = self.cards[:start_idx]  # Обновляем список карт в столбце
        return removed_cards  # Возвращаем удаленные карты
    def draw(self, screen, start_pos):
        x, y = start_pos  # Начальная позиция для рисования карт в столбце
        for card in self.cards:  # Для каждой карты в столбце
            card.draw(screen, (x, y))  # Рисуем карту
            y += 30  # Смещение для следующей карты в столбце
    def get_top_card(self):
        if self.cards:  # Если в столбце есть карты
            return self.cards[-1]  # Возвращаем верхнюю карту в столбце
        return None  # Если столбец пуст, возвращаем None

# Класс для представления базовой стопки (фундамента)
class Foundation:
    def __init__(self):
        self.cards = []  # Список карт в базовой стопке
    def add_card(self, card):
        self.cards.append(card)  # Добавляем карту в базовую стопку
    def get_top_card(self):
        if self.cards:  # Если в базовой стопке есть карты
            return self.cards[-1]  # Возвращаем верхнюю карту в базовой стопке
        return None  # Если стопка пуста, возвращаем None
    def can_add_card(self, card):
        if not self.cards:  # Если в стопке нет карт
            return card.value == 1  # Туз должен быть первым
        top_card = self.get_top_card()  # Получаем верхнюю карту в стопке
        return card.suit == top_card.suit and card.value == top_card.value + 1  # Карты должны быть одной масти и возрастающего значения
    def draw(self, screen, pos):
        x, y = pos  # Позиция для рисования базовой стопки
        if self.cards:  # Если в стопке есть карты
            self.cards[-1].draw(screen, (x, y))  # Рисуем верхнюю карту в стопке

# Класс для представления колоды карт
class Deck:
    def __init__(self):
        self.cards = []  # Список карт в колоде
    def add_card(self, card):
        self.cards.append(card)  # Добавляем карту в колоду
    def draw(self, screen, pos):
        x, y = pos  # Позиция для рисования колоды
        if self.cards:  # Если в колоде есть карты
            back_image_rect = back_image.get_rect(topleft=(x, y))  # Получаем прямоугольник изображения обратной стороны карты
            screen.blit(back_image, back_image_rect)  # Рисуем обратную сторону карты
    def draw_card(self):
        if self.cards:  # Если в колоде есть карты
            return self.cards.pop()  # Возвращаем верхнюю карту из колоды
    def refill(self, draw_pile):
        while draw_pile:  # Пока есть карты в стопке вытянутых карт
            card = draw_pile.pop()  # Берем карту из стопки вытянутых карт
            card.face_up = False  # Переворачиваем карту лицевой стороной вниз
            self.cards.append(card)  # Возвращаем карту в колоду

# Подготовка колоды и раздача карт по столбцам
columns = [Column() for i in range(7)]
foundations = [Foundation() for i in range(4)]
deck = Deck()
draw_pile = []
colors = {'hearts': 'red', 'diamonds': 'red', 'clubs': 'black', 'spades': 'black'}
deck.cards = [Card(f"{value}_of_{suit}", card_images[f"{value}_of_{suit}"], values.index(value) + 1, suit, colors[suit])
              for suit in suits for value in values]
random.shuffle(deck.cards)
for i in range(7):
    for j in range(i + 1):
        card = deck.cards.pop()
        if j == i:
            card.face_up = True
        columns[i].add_card(card)

# Переменные для отслеживания выбранной карты
selected_cards = []
selected_column = None
selected_deck_card = None
selected_foundation = None
selected_foundation_card = None
offset_x, offset_y = 0, 0

def can_place_card(card_to_place, target_card):
    return card_to_place.value == target_card.value - 1 and card_to_place.color != target_card.color

def handle_mouse_button_up(mouse_x, mouse_y):
    global selected_cards, selected_column, selected_deck_card, selected_foundation, selected_foundation_card
    if selected_cards:  # Если есть выбранные карты из столбца
        card_placed = False  # Флаг, указывающий на успешное размещение карты
        for foundation in foundations:  # Перебираем все базовые стопки
            if foundation.can_add_card(selected_cards[0]) and len(selected_cards) == 1:  # Проверяем, можно ли добавить карту в базовую стопку
                foundation.add_card(selected_cards[0])
                card_placed = True  # Устанавливаем флаг успешного размещения
                break  # Выходим из цикла, так как карты успешно размещены
        if not card_placed:  # Если карты не были размещены в столбцах
            for column in columns:  # Перебираем все столбцы
                if column == selected_column:  # Пропускаем столбец, из которого были взяты карты
                    continue
                if not column.cards:  # Если столбец пуст
                    if selected_cards[0].value == 13:  # Короля можно перемещать на пустое место
                        column.cards.extend(selected_cards)  # Добавляем карты в столбец
                        card_placed = True  # Устанавливаем флаг успешного размещения
                        break  # Выходим из цикла, так как карты успешно размещены
                else:
                    top_card = column.get_top_card()  # Получаем верхнюю карту в текущем столбце
                    if can_place_card(selected_cards[0],
                                      top_card):  # Проверяем, можно ли поместить выбранную карту на верхнюю карту столбца
                        column.cards.extend(selected_cards)  # Добавляем карты в столбец
                        card_placed = True  # Устанавливаем флаг успешного размещения
                        break  # Выходим из цикла, так как карты успешно размещены
        if card_placed:  # Если карты были успешно размещены
            selected_column.remove_cards(len(selected_column.cards))  # Удаляем карты из исходного столбца
            if selected_column.cards and not selected_column.get_top_card().face_up:  # Если в столбце остались карты и верхняя карта лицевой стороной вниз
                selected_column.get_top_card().face_up = True  # Переворачиваем верхнюю карту лицевой стороной вверх
        else:  # Если карты не были размещены
            selected_column.cards.extend(selected_cards)  # Возвращаем карты в исходный столбец
        selected_cards = []  # Очищаем список выбранных карт
        selected_column = None  # Сбрасываем выбранный столбец
    elif selected_deck_card:  # Если была выбрана карта из колоды
        card_placed = False  # Флаг, указывающий на успешное размещение карты
        for foundation in foundations:  # Перебираем все базовые стопки
            if foundation.can_add_card(selected_deck_card):  # Проверяем, можно ли добавить карту в базовую стопку
                foundation.add_card(selected_deck_card)  # Добавляем карту в базовую стопку
                card_placed = True  # Устанавливаем флаг успешного размещения
                break  # Выходим из цикла, так как карта успешно размещена
        if not card_placed:  # Если карта не была размещена в столбцах
            for column in columns:  # Перебираем все столбцы
                if not column.cards:  # Если столбец пуст
                    if selected_deck_card.value == 13:  # Короля можно перемещать на пустое место
                        column.add_card(selected_deck_card)  # Добавляем карту в столбец
                        card_placed = True  # Устанавливаем флаг успешного размещения
                        break  # Выходим из цикла, так как карта успешно размещена
                else:
                    top_card = column.get_top_card()  # Получаем верхнюю карту в текущем столбце
                    if can_place_card(selected_deck_card, top_card):  # Проверяем, можно ли поместить выбранную карту на верхнюю карту столбца
                        column.add_card(selected_deck_card)  # Добавляем карту в столбец
                        card_placed = True  # Устанавливаем флаг успешного размещения
                        break  # Выходим из цикла, так как карта успешно размещена
        if not card_placed:  # Если карта не была размещена
            draw_pile.append(selected_deck_card)  # Возвращаем карту в стопку вытянутых карт
        selected_deck_card = None  # Сбрасываем выбранную карту из колоды
    elif selected_foundation_card:  # Если была выбрана карта из базовой стопки
        card_placed = False  # Флаг, указывающий на успешное размещение карты
        for column in columns:  # Перебираем все столбцы
            if not column.cards:  # Если столбец пуст
                if selected_foundation_card.value == 13:  # Короля можно перемещать на пустое место
                    column.add_card(selected_foundation_card)  # Добавляем карту в столбец
                    card_placed = True  # Устанавливаем флаг успешного размещения
                    break  # Выходим из цикла, так как карта успешно размещена
            else:
                top_card = column.get_top_card()  # Получаем верхнюю карту в текущем столбце
                if can_place_card(selected_foundation_card,
                                  top_card):  # Проверяем, можно ли поместить выбранную карту на верхнюю карту столбца
                    column.add_card(selected_foundation_card)  # Добавляем карту в столбец
                    card_placed = True  # Устанавливаем флаг успешного размещения
                    break  # Выходим из цикла, так как карта успешно размещена
        if not card_placed:  # Если карта не была размещена в столбцах
            for foundation in foundations:  # Перебираем все базовые стопки
                if foundation.can_add_card(
                        selected_foundation_card):  # Проверяем, можно ли добавить карту в базовую стопку
                    foundation.add_card(selected_foundation_card)  # Добавляем карту в базовую стопку
                    card_placed = True  # Устанавливаем флаг успешного размещения
                    break  # Выходим из цикла, так как карта успешно размещена
        if not card_placed:  # Если карта не была размещена
            selected_foundation.add_card(selected_foundation_card)  # Возвращаем карту в исходную базовую стопку
        selected_foundation_card = None  # Сбрасываем выбранную карту из базовой стопки
        selected_foundation = None  # Сбрасываем выбранную базовую стопку

# Функция для отображения победного экрана
def show_victory_screen(screen):
    vict_scr = pygame.image.load("assets/victory_screen.png")
    screen.blit(vict_scr, (0, 0))
    button_rect = pygame.Rect(320, 420, 320, 160)
    ng_btt = pygame.image.load("assets/new_game_button.png")
    screen.blit(ng_btt, (320, 420))
    pygame.display.flip()
    return button_rect

# Функция для отрисовки кнопки перезапуска игры
def draw_restart_button():
    button_rect = pygame.Rect(750, 70, 150, 50)
    rest_btt = pygame.image.load("assets/restart_button.png")
    screen.blit(rest_btt, (750, 70))
    return button_rect

# Функция для проверки победы
def check_victory(foundations):
    return all(len(foundation.cards) == 13 for foundation in foundations)


while True:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            deck_rect = back_image.get_rect(topleft=(50, 50))  # Получение области колоды
            if deck_rect.collidepoint(mouse_x, mouse_y):  # По колоде ли клик
                if deck.cards:  # Если есть карты в колоде - вытягивается ещё одна
                    drawn_card = deck.draw_card()
                    drawn_card.face_up = True
                    draw_pile.append(drawn_card)
                else:  # Если нет - колода обратно заполняется
                    deck.refill(draw_pile)
                continue
            if draw_pile:  # Если стопка вытянутых карт не пуста
                drawn_card_rect = draw_pile[-1].image.get_rect(topleft=(150, 50))
                if drawn_card_rect.collidepoint(mouse_x, mouse_y):  # Проверка нажатия на стопку вытянутых карт
                    selected_deck_card = draw_pile.pop()  # Выбирается карта из этой стопки
                    break
            for column in columns:
                if column.cards:
                    for idx, card in enumerate(column.cards):  # Пара из карты в столбце и её индекса
                        card_rect = card.image.get_rect(topleft=(50 + columns.index(column) * 100, 150 + 30 * idx))  # Область нажатия на карту
                        if card_rect.collidepoint(mouse_x, mouse_y) and card.face_up:
                            selected_cards = column.cards[idx:]  # Выбор карты или группы карт из столбца, начиная с выбранной
                            selected_column = column  # Запись выбранного столбца
                            offset_x = card_rect.x - mouse_x
                            offset_y = card_rect.y - mouse_y
                            column.cards = column.cards[:idx]  # Удаление выбранных карт из столбца
                            break  # Выход из цикла for
                    if selected_cards:  # Если карты выбраны, закончить обработку нажатия кнопки мыши
                        break
            for foundation in foundations:  # Проходимся по базовым стопкам
                if foundation.cards:  # Если есть карты в базовой стопке
                    top_card = foundation.get_top_card()
                    card_rect = top_card.image.get_rect(topleft=(300 + foundations.index(foundation) * 100, 50))
                    if card_rect.collidepoint(mouse_x, mouse_y):  # Если выбрана карта из базовой стопки
                        selected_foundation_card = foundation.cards.pop()
                        selected_foundation = foundation
                        offset_x = card_rect.x - mouse_x
                        offset_y = card_rect.y - mouse_y
                        break

        elif event.type == pygame.MOUSEBUTTONUP:  # Обработка отпускания кнопки мыши
            handle_mouse_button_up(mouse_x, mouse_y)

        elif event.type == pygame.MOUSEMOTION:  # Обработка движения мыши
            if selected_cards or selected_deck_card or selected_foundation_card:
                mouse_x, mouse_y = event.pos  # Если карты выбраны, обновляются координаты мыши для перетаскивания карт

    screen.blit(backgr,(0,0))  # Отрисовка фона
    deck.draw(screen, (50, 50))  # Отрисовка колоды и стопки вытянутых карт
    if draw_pile:
        draw_pile[-1].draw(screen, (150, 50))
    foundation_x = 300  # Отрисовка базовых стопок
    for foundation in foundations:
        foundation.draw(screen, (foundation_x, 50))
        foundation_x += 100
    start_x = 50  # Отрисовка карт в столбцах
    for column in columns:
        column.draw(screen, (start_x, 150))
        start_x += 100
    if selected_cards:  # Отрисовка перемещаемых карт
        for idx, card in enumerate(selected_cards):
            screen.blit(card.image, (mouse_x + offset_x, mouse_y + offset_y + 30 * idx))
    elif selected_deck_card:
        screen.blit(selected_deck_card.image, (mouse_x + offset_x, mouse_y + offset_y))
    elif selected_foundation_card:
        screen.blit(selected_foundation_card.image, (mouse_x + offset_x, mouse_y + offset_y))

    if check_victory(foundations):  # Проверка на победу
        button_rect = show_victory_screen(screen)
        pygame.display.flip()  # Обновляем экран, чтобы показать победный экран
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        # Начать новую игру
                        deck = Deck()
                        columns = [Column() for _ in range(7)]
                        foundations = [Foundation() for _ in range(4)]
                        draw_pile = []

                        deck.cards = [
                            Card(f"{value}_of_{suit}", card_images[f"{value}_of_{suit}"], values.index(value) + 1, suit,
                                 colors[suit]) for suit in suits for value in values]
                        random.shuffle(deck.cards)

                        for i in range(7):
                            for j in range(i + 1):
                                card = deck.cards.pop()
                                if j == i:
                                    card.face_up = True
                                columns[i].add_card(card)
                        break  # Выйти из внутреннего цикла и вернуться в основной игровой цикл
            else:
                continue  # Это позволяет остаться в этом внутреннем цикле, если не нажата кнопка "Новая игра"
            break  # Выйти из внутреннего цикла, если нажата кнопка "Новая игра"

     # Обработка кнопки перезапуска игры
    restart = draw_restart_button()
    if event.type == pygame.MOUSEBUTTONDOWN:
        if restart.collidepoint(event.pos):
            # Начать новую игру
            deck = Deck()
            columns = [Column() for _ in range(7)]
            foundations = [Foundation() for _ in range(4)]
            draw_pile = []
            deck.cards = [
                Card(f"{value}_of_{suit}", card_images[f"{value}_of_{suit}"], values.index(value) + 1, suit,
                     colors[suit]) for suit in suits for value in values]
            random.shuffle(deck.cards)
            for i in range(7):
                for j in range(i + 1):
                    card = deck.cards.pop()
                    if j == i:
                        card.face_up = True
                    columns[i].add_card(card)

    pygame.display.flip()
