import pygame
import pygame_gui as pgui
import utypes as tp
import random
import re
import copy


def generate_ans(width, height):
    """Генерируем заполненую таблицу."""

    table = [[] for _ in range(height)]
    for i in range(height):
        letters = [j for j in tp.LETTERS[:width]]  # Создаем новый массив букв
        table[i] = [[f'{i + 1}{letters.pop(random.randint(0, len(letters) - 1))}'] for _ in
                    range(width)]  # Заполняем строки параметрами НОМЕР_СТРОКИ+БУКВА

    completed_cells = []
    for x in range(width):  # Создаем список нетронутых клеток
        completed_cells.append([])
        for y in range(height):
            completed_cells[-1].append(y)

    return table, completed_cells


def check_possibility(completed_cells):
    """Проверка на возможность использования разных типов утверждений."""

    """
    Возможные конфигурации:
    000-только 1 тип
    100-только 2 тип
    010-только 3 тип
    110-2 и 3 тип
    011-3 и 4 тип
    111-все типы (кроме 1)
    """

    n = 0
    result = '000'
    for i in range(len(completed_cells)):
        if len(completed_cells[i]) >= 2:  # Проверка 2 типа
            result = '1' + result[1:]
            n += len(completed_cells[i])

        if i and completed_cells[i] and completed_cells[i - 1]:  # Проверка 3 типа
            result = result[:1] + '1' + result[2:]
            n += len(completed_cells[i])
            if i < len(completed_cells) - 1 and completed_cells[i + 1]:  # Проверка 4 типа
                result = result[:2] + '1'

    if n < 2:
        return '000'

    return result


def create_condition(possibility, table, completed_cells):

    """Генерация новых утверждений.
       Общий алгоритм:
       Создовая новое условие, привязываем одну завершенную клетку к другой (или к дому).
       Теперь ее значение можно вычислить через другую клетку => можно убирать ее из списка завершенных клеток.
       Повторяем пока не закончатся завершенные клетки.
    """

    height = len(table)
    width = len(table[0])
    new_condition = []
    new_question = ''
    new_answer = ''
    if '1' in possibility:  # Если доступны типы с 2 по 4.
        if possibility == '110':
            roll = random.choice([2, 2, 2, 3])
        elif possibility == '011':
            roll = random.choice([3, 4])
        else:
            roll = random.choice([2, 2, 2, 2, 3, 3, 4])

        # Так как порядок вариантов клеток не менялся с момента создания таблицы, то на первом месте в вариантах клетки сейчас находится ответ для нее.

        if roll == 2 and int(possibility[
                                 0]) or possibility == '100':  # Если выпал 2 тип и он разрешен, или он единственный разрешенный тип.
            x = random.randint(0, width - 1)
            while len(completed_cells[x]) < 2:  # Пока в столбце не будет 2 или больше завершенных клеток реролим x.
                x = random.randint(0, width - 1)
            y2 = completed_cells[x].pop(random.randint(0, len(
                completed_cells[x]) - 1))  # Удаляем вторую клетку с координатами x;y2 из массива завершенных клеток.
            y1 = completed_cells[x][random.randint(0, len(
                completed_cells[x]) - 1)]  # К первой клетке мы прявязали утверждением вторую, ее удалять не надо.
            k1, k2 = table[y1][x][0], table[y2][x][0]  # Смотрим чему действительно равны параметры в клетках.
            new_condition = f'2;{k1};{k2}'  # Создаем условие
            new_question = f'{x + 1};{y2 + 1}'  # Создаем вопрос
            new_answer = k2  # Запоминаем ответ
            for i in range(width):
                if k2 not in table[y2][i]:
                    table[y2][i].append(k2)  # Добавляем параметр 2-ой клетки в варианты остальных клеток строки.

        elif roll == 3 and int(possibility[
                                   1]) or possibility == '010':  # Если выпал 3 тип и он разрешен, или он единственный разрешенный тип.
            x1 = random.randint(0, width - 1)
            if x1 == 0:
                x2 = 1
            elif x1 == width - 1:
                x2 = width - 2
            else:
                x2 = x1 - random.choice([-1, 1])
            while not completed_cells[x1] or not completed_cells[x2]:  # Пока в двух соседних слобцах не будут завершенные клетки реролим x.
                x1 = random.randint(0, width - 1)
                if x1 == 0:
                    x2 = 1
                elif x1 == width - 1:  # Если х1 крайний, то x2 однозначно задан
                    x2 = width - 2
                else:  # Иначе все равно, где будет х2 относительно х1
                    x2 = x1 - random.choice([-1, 1])
            y2 = completed_cells[x2].pop(random.randint(0, len(
                completed_cells[x2]) - 1))  # Удаляем вторую клетку с координатами x2;y2 из массива завершенных клеток.
            y1 = completed_cells[x1][random.randint(0, len(
                completed_cells[x1]) - 1)]  # К первой клетке мы прявязали утверждением вторую, ее удалять не надо.
            if x1 - x2 == 1:  # Определяем расположение х1 относительно х2
                place = 'справа'
            else:
                place = 'слева'
            k1, k2 = table[y1][x1][0], table[y2][x2][0]  # Смотрим чему действительно равны параметры в клетках.
            new_condition = f'3;{k1};{place};{k2}'  # Создаем условие
            new_question = f'{x2 + 1};{y2 + 1}'  # Создаем вопрос
            new_answer = k2  # Запоминаем ответ
            for i in range(width):
                if k2 not in table[y2][i]:
                    table[y2][i].append(k2)  # Добавляем параметр 2-ой клетки в варианты остальных клеток строки.

        elif roll == 4 and int(possibility[2]):  # Если выпал 4 тип и он разрешен.
            x1 = random.randint(0, width - 1)
            if x1 == 0:
                x2 = 1
            elif x1 == width - 1:
                x2 = width - 2
            else:
                x2 = x1 - random.choice([-1, 1])
            while not completed_cells[x1] or not completed_cells[x2]:  # Пока в двух соседних слобцах не будут завершенные клетки реролим x.
                x1 = random.randint(0, width - 1)
                if x1 == 0:
                    x2 = 1
                elif x1 == width - 1:  # Если х1 крайний, то x2 однозначно задан
                    x2 = width - 2
                else:  # Иначе все равно, где будет х2 относительно х1
                    x2 = x1 - random.choice([-1, 1])
            y2 = completed_cells[x2].pop(random.randint(0, len(
                completed_cells[x2]) - 1))  # Удаляем вторую клетку с координатами x2;y2 из массива завершенных клеток.
            y1 = completed_cells[x1][random.randint(0, len(
                completed_cells[x1]) - 1)]  # К первой клетке мы прявязали утверждением вторую, ее удалять не надо.

            k1, k2 = table[y1][x1][0], table[y2][x2][0]  # Смотрим чему действительно равны параметры в клетках.
            new_condition = f'4;{k1};{k2}'  # Создаем условие
            new_question = f'{x2 + 1};{y2 + 1}'  # Создаем вопрос
            new_answer = k2  # Запоминаем ответ
            for i in range(width):
                if k2 not in table[y2][i]:
                    table[y2][i].append(k2)  # Добавляем параметр 2-ой клетки в варианты остальных клеток строки.


    elif possibility == '000':  # Если доступен только 1 тип.
        completed_cells_exist = True
        while completed_cells_exist:  # Пока существуют завершенные клетки
            x = random.randint(0, width - 1)
            while not completed_cells[x]:  # Пока не встретим столбец с завершенной клеткой реролим х.
                x = random.randint(0, width - 1)
            y = completed_cells[x].pop(random.randint(0, len(completed_cells[x]) - 1))  # Удаляем вторую клетку с координатами x;y из массива завершенных клеток. Она будет привязана к номеру дома напрямую.
            k = table[y][x][0]  # Смотрим чему действительно равен параметр в клетке.
            new_condition.append(f'1;{x + 1};{k}')  # Создаем условие
            new_question = f'{x + 1};{y + 1}'  # Создаем вопрос
            new_answer = k  # Запоминаем ответ
            for i in range(width):
                if k not in table[y][i]:
                    table[y][i].append(k)  # Добавляем параметр клетки в варианты остальных клеток строки.

            completed_cells_exist = False
            for i in completed_cells:  # Проверяем остались ли завершенные клетки
                if i:
                    completed_cells_exist = True
        return table, completed_cells, new_condition, new_question, new_answer

    return table, completed_cells, [new_condition], new_question, new_answer


def convert(string):
    global width, height
    """Делает вывод красивым."""

    options = {}
    for i in range(1, height + 1):
        options.update({f'{i}': f'{i}'})
        options.update({f'{i}{j}': f'{i}{j}' for j in tp.LETTERS[:width]})
    with open('Шаблоны.txt', 'r', encoding='utf-8') as file:
        i = 1
        for line in file:
            line = line.replace(' ', '').strip('\n')
            options.update({f'{i}': f'{line.split(":")[0]}'})
            for j, option in enumerate(line.split(':')[1].split(',')):
                options.update({f'{i}{tp.LETTERS[j]}': f'{option}'})
            i += 1
    parts = string.split(';')
    if len(parts) == 2 and parts[1][-1].isalpha():
        y = str(int(re.search(r'\d+', parts[1]).group(0)))
        return f'В доме с номером {parts[0]} {options[y]} - {options[parts[1]]}.'  # Вывод ответа
    elif len(parts) == 2 and not parts[1][-1].isalpha():
        y = str(int(re.search(r'\d+', parts[1]).group(0)))
        return f'Что в доме с номером {parts[0]} в параметре {options[y]}?'  # Вывод вопроса
    elif parts[0] == '0':
        start = f'В ряд стоят {parts[1]} дома(ов) с {parts[2]} параметрами(ом).\n'  # Вывод условия
        end = ''
        for i in range(1, height + 1):
            end += options[str(i)] + ': '
            for j in tp.LETTERS[:width]:
                end += options[f'{i}{j}'] + ', '
            end = end[:-2] + '\n'
        # with open('Шаблоны.txt', 'r', encoding='utf-8') as file:
        #     i = 1
        #     for line in file:
        #         if i <= int(parts[2]):
        #             line = line.split(',')
        #             new_part = ''.join(line[:int(parts[1])])
        #             end += new_part[:new_part.index(' ') + 1] + new_part[new_part.index(' ') + 1:].replace(' ', ', ') + '\n'
        #         i += 1
        start += end
        return start
    elif parts[0] == '1':
        y = str(int(re.search(r'\d+', parts[2]).group(0)))
        return f'В доме номер {parts[1]} {options[y]} - {options[parts[2]]}.'  # Вывод 1 типа
    elif parts[0] == '2':
        y1 = str(int(re.search(r'\d+', parts[1]).group(0)))
        y2 = str(int(re.search(r'\d+', parts[2]).group(0)))
        return f'В доме, в котором {options[y1]} - {options[parts[1]]}, {options[y2]} - {options[parts[2]]}.'  # Вывод 2 типа
    elif parts[0] == '3':
        y1 = str(int(re.search(r'\d+', parts[1]).group(0)))
        y2 = str(int(re.search(r'\d+', parts[3]).group(0)))
        return f'Дом, в котором {options[y1]} - {options[parts[1]]}, {parts[2]} от дома, в котором {options[y2]} - {options[parts[3]]}.'  # Вывод 3 типа
    elif parts[0] == '4':
        y1 = str(int(re.search(r'\d+', parts[1]).group(0)))
        y2 = str(int(re.search(r'\d+', parts[2]).group(0)))
        return f'Дом, в котором {options[y1]} - {options[parts[1]]}, соседний с домом, в котором {options[y2]} - {options[parts[2]]}.'  # Вывод 4 типа


def save_result(conditions, questions, answers):
    """Сохранение результатов в файл."""

    file = open(r'Задачи\Условие.txt', 'w')
    for i in conditions:
        file.write(convert(i) + '\n')
    file.write('\n')

    for i in questions:
        file.write(convert(i) + '\n')
    file.close()

    file = open(r'Задачи\Ответ.txt', 'w')
    for i in questions:
        file.write(convert(i) + '\n')
    file.write('\nОтвет: \n')

    for i in answers:
        file.write(convert(i) + '\n')
    file.close()


def solve_puzzle(conditions, questions, table, max_deep):
    """Решает задачу по условиям."""

    uncompleted_cells = 0
    deep = max_deep
    height = len(table)
    width = len(table[0])
    completed_cells = [[] for _ in range(width)]
    used_conditions = []
    something_happened = True
    answer = []

    while something_happened:
        something_happened = False
        for condition in conditions:
            if condition[0] == '1':
                used_conditions.append(condition)
                k = condition.split(';')[2]
                x = int(condition.split(';')[1]) - 1
                y = int(re.search(r'\d+', condition.split(';')[2]).group(0)) - 1
                table[y][x] = [k]
                something_happened = True
                completed_cells[x].append(y)
                for i in range(width):
                    if y not in completed_cells[i]:
                        try:
                            table[y][i].pop(table[y][i].index(k))
                        except ValueError:
                            pass

            if condition[0] == '2':
                k1 = condition.split(';')[1]
                k2 = condition.split(';')[2]
                y1 = int(re.search(r'\d+', k1).group(0)) - 1
                y2 = int(re.search(r'\d+', k2).group(0)) - 1
                for x in range(width):
                    if len(table[y1][x]) == 1 and table[y1][x][0] == k1:
                        table[y2][x] = [k2]
                        something_happened = True
                        used_conditions.append(condition)
                        completed_cells[x].append(y2)
                        for i in range(width):
                            if y2 not in completed_cells[i]:
                                try:
                                    table[y2][i].pop(table[y2][i].index(k2))
                                except ValueError:
                                    pass

                    if len(table[y2][x]) == 1 and table[y2][x][0] == k2:
                        table[y1][x] = [k1]
                        something_happened = True
                        used_conditions.append(condition)
                        completed_cells[x].append(y1)
                        for i in range(width):
                            if y1 not in completed_cells[i]:
                                try:
                                    table[y1][i].pop(table[y1][i].index(k1))
                                except ValueError:
                                    pass

            if condition[0] == '3':
                k1 = condition.split(';')[1]
                place = condition.split(';')[2]
                k2 = condition.split(';')[3]
                y1 = int(re.search(r'\d+', k1).group(0)) - 1
                y2 = int(re.search(r'\d+', k2).group(0)) - 1

                for x in range(width):
                    if len(table[y1][x]) == 1 and table[y1][x][0] == k1:
                        if place == "слева":
                            x2 = x + 1
                        else:
                            x2 = x - 1
                        if x2 >= width or x2 < 0:
                            return False, answer, table
                        table[y2][x2] = [k2]
                        something_happened = True
                        used_conditions.append(condition)
                        completed_cells[x2].append(y2)
                        for i in range(width):
                            if y2 not in completed_cells[i]:
                                try:
                                    table[y2][i].pop(table[y2][i].index(k2))
                                except ValueError:
                                    pass

                    if len(table[y2][x]) == 1 and table[y2][x][0] == k2:
                        if place == "слева":
                            x1 = x - 1
                        else:
                            x1 = x + 1
                        if x1 >= width or x1 < 0:
                            return False, answer, table
                        table[y1][x1] = [k1]
                        something_happened = True
                        used_conditions.append(condition)
                        completed_cells[x1].append(y1)
                        for i in range(width):
                            if y1 not in completed_cells[i]:
                                try:
                                    table[y1][i].pop(table[y1][i].index(k1))
                                except ValueError:
                                    pass
            if condition[0] == '4':
                k1 = condition.split(';')[1]
                k2 = condition.split(';')[2]
                y1 = int(re.search(r'\d+', k1).group(0)) - 1
                y2 = int(re.search(r'\d+', k2).group(0)) - 1

                for x in range(width):
                    if len(table[y1][x]) == 1 and table[y1][x][0] == k1:
                        something_happened = True
                        used_conditions.append(condition)
                        for i in range(width):
                            if y2 not in completed_cells[i] and abs(x - i) > 1:
                                try:
                                    table[y2][i].pop(table[y2][i].index(k2))
                                except ValueError:
                                    pass
                    if len(table[y2][x]) == 1 and table[y2][x][0] == k1:
                        something_happened = True
                        used_conditions.append(condition)
                        for i in range(width):
                            if y1 not in completed_cells[i] and abs(x - i) > 1:
                                try:
                                    table[y1][i].pop(table[y1][i].index(k1))
                                except ValueError:
                                    pass

        for used_condition in used_conditions:
            try:
                conditions.pop(conditions.index(used_condition))
            except ValueError:
                pass
        used_conditions = []

        for x in range(width):
            for y in range(height):
                if len(table[y][x]) == 1 and y not in completed_cells[x]:
                    completed_cells[x].append(y)
                    something_happened = True
                    for i in range(width):
                        if y not in completed_cells[i]:
                            try:
                                table[y][i].pop(table[y][i].index(table[y][x][0]))
                            except ValueError:
                                pass

    for x in range(width):
        for y in range(height):
            if len(table[y][x]) != 1:
                uncompleted_cells += 1

    if uncompleted_cells > 0 and not conditions:
        return False, answer, table
    elif uncompleted_cells > 0 and conditions:
        is_solved, table, deep, answer = brute_force_search(copy.deepcopy(table), conditions.copy(), questions.copy(),
                                                            deep)
        if is_solved:
            return True, answer, table
        else:
            return False, answer, table

    for question in questions:
        x = int(question.split(';')[0]) - 1
        y = int(question.split(';')[1]) - 1
        answer.append(f'{x + 1};{table[y][x][0]}')

    return True, answer, table


def removing_excess(conditions, questions, table):
    """Убирает избытычность условий."""

    new_conditions = conditions.copy()
    empty_table = copy.deepcopy(table)
    is_solved, new_answers, new_table = solve_puzzle(new_conditions.copy(), questions.copy(), empty_table, 0)
    while is_solved:  # Если смогло решить.
        conditions = new_conditions.copy()
        for i in conditions:
            new_conditions = conditions.copy()
            new_conditions.remove(i)  # Удаляем 1 из условий.
            empty_table = copy.deepcopy(table)
            is_solved, new_answers, new_table = solve_puzzle(new_conditions.copy(), questions.copy(), empty_table, 0)  # Смотрим, смогло ли решить?
            if is_solved:  # Если смогло запомним резульат.
                break
    return conditions  # Если ни разу решилось то возвращаем.


def brute_force_search(table, condition, questions, deep):
    """
    Подставляет один из вариантов и пытается решить.
    Есть ограничение по глубине.
    """

    answer = []
    new_table = copy.deepcopy(table)
    if not deep:
        return False, new_table, deep, answer
    height = len(new_table)
    width = len(new_table[0])
    min_k = width + 1
    new_cell = (-1, -1)

    for y in range(height):
        for x in range(width):
            if 1 < len(new_table[y][x]) <= min_k:
                min_k = len(new_table[y][x])
                new_cell = (x, y)

    x, y = new_cell

    for option in table[y][x]:
        backup = copy.deepcopy(new_table)
        new_table[y][x] = [option]

        for x in range(width):
            for y in range(height):
                if len(new_table[y][x]) == 1:
                    remove = new_table[y][x][0]
                    for i in range(width):
                        if i != x:
                            try:
                                new_table[y][i].remove(remove)
                            except ValueError:
                                pass

        is_solved, answer, _ = solve_puzzle(condition, questions, new_table, deep - 1)
        if is_solved:
            return True, new_table, deep, answer
        else:
            new_table = copy.deepcopy(backup)

    return False, copy.deepcopy(table), deep - 1, answer


def generate_puzzle(width=4, height=3):
    """Основное тело программы."""

    table, competed_cells = generate_ans(width, height)
    competed_table = copy.deepcopy(table)
    conditions = []
    questions = []
    answers = []
    possibility = '110'

    while '1' in possibility:
        possibility = check_possibility(competed_cells)
        table, competed_cells, new_condition, new_question, new_answer = create_condition(possibility, table, competed_cells)
        for i in new_condition:
            conditions.append(i)
        if len(questions) < 2:
            questions.append(new_question)
            answers.append(f'{new_question.split(";")[0]};{new_answer}')

    for y in range(len(table)):
        for x in range(len(table[0])):
            random.shuffle(table[y][x])

    print(len(conditions))
    random.shuffle(conditions)
    empty_table = copy.deepcopy(table)
    conditions = removing_excess(conditions, questions, empty_table).copy()
    conditions.insert(0, f'0;{len(table[0])};{len(table)}')  # Добвляем вводную часть.
    is_solved, new_answers, new_table = solve_puzzle(conditions.copy(), questions.copy(), table, 0)
    save_result(conditions, questions, answers)
    print(len(conditions))

    print('________________Если совпали - хорошо___________________')
    print(competed_table)
    print(new_table)
    print(answers)
    print(new_answers)


def start_bf(width, height):
    start_b.disable()
    width_input.disable()
    height_input.disable()
    generate_puzzle(width, height)
    start_b.enable()
    width_input.enable()
    height_input.enable()

def get_values():
    if width_input.text == '':
        width = 4
    else:
        width = int(width_input.text)
    if height_input.text == '':
        height = 3
    else:
        height = int(height_input.text)
    return width, height


pygame.init()
pygame.font.init()
out_font = pygame.font.Font(None, 30)
manager = pgui.UIManager((tp.WIDTH, tp.HEIGHT))
screen = pygame.display.set_mode((tp.WIDTH, tp.HEIGHT))
pygame.display.set_caption("Генератор загадок Эйнштейна")
clock = pygame.time.Clock()
screen.fill(tp.BG_COLOR)

start_b = pgui.elements.UIButton(relative_rect=pygame.Rect((125, 20), tp.BUTTON_SIZE),
                                 text='Начать',
                                 manager=manager)
start_b.colours['normal_text'] = pygame.Color(tp.WHITE)
start_b.colours['normal_bg'] = pygame.Color((40, 40, 40, 255))
start_b.rebuild()

width_input = pgui.elements.UITextEntryLine(relative_rect=pygame.Rect((350, 90), tp.INPUT_SIZE),
                                            manager=manager)
height_input = pgui.elements.UITextEntryLine(relative_rect=pygame.Rect((350, 160), tp.INPUT_SIZE),
                                             manager=manager)



width_label = pgui.elements.UILabel(relative_rect=pygame.Rect((125, 90), (175, 30)), text='Введите кол-во домов', manager=manager)
width_label.bg_colour = pygame.Color(tp.BG_COLOR)
width_label.text_colour = pygame.Color(tp.BLACK)
width_label.font = pygame.font.Font('arial.ttf', 16)
width_label.rebuild()

height_label = pgui.elements.UILabel(relative_rect=pygame.Rect((125, 160), (225, 30)), text='Введите кол-во параметров', manager=manager)
height_label.bg_colour = pygame.Color(tp.BG_COLOR)
height_label.text_colour = pygame.Color(tp.BLACK)
height_label.font = pygame.font.Font('arial.ttf', 16)
height_label.rebuild()


width_input.set_allowed_characters(tp.WHITE_LIST)
height_input.set_allowed_characters(tp.WHITE_LIST)
width_input.set_text_length_limit(2)
height_input.set_text_length_limit(2)


run = True
while run:
    time_delta = clock.tick(60) / 1000.0
    width, height = get_values()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        manager.process_events(event)
        if event.type == pygame.USEREVENT:
            if event.user_type == pgui.UI_BUTTON_PRESSED:  # обработка нажатий на кнопки
                if event.ui_element == start_b:
                    start_bf(width, height)
    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()
