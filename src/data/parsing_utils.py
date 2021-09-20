def getPage(page, area):
    """
    Создаем метод для получения страницы со списком вакансий.
    Аргументы:
        page - Индекс страницы
        area - Индекс региона
    """
    # Справочник для параметров GET-запроса
    params = {
        'area': area,  # Поиск ощуществляется по вакансиям города area
        'page': page,  # Индекс страницы поиска на HH
        'per_page': 100  # Кол-во вакансий на 1 странице
    }
    req = requests.get('https://api.hh.ru/vacancies', params)  # Посылаем запрос к API
    data = req.content.decode()  # Декодируем его ответ, чтобы Кириллица отображалась корректно
    req.close()
    return data

def getAllPages(df_areas):
    """
    Создаем метод для получения 20 * len(df_areas) страниц с вакансиями.
    Аргумент:
        df_areas - датафрейм с id регионов
    """
    areas = len(df_areas)
    for i in range(areas):
        area = df_areas['id'][i]
        print(area)
        # Считываем первые 2000 вакансий
        for page in range(20):
            # Преобразуем текст ответа запроса в справочник Python
            try:
                jsObj = json.loads(getPage(page, area))
                # Сохраняем файлы в папку {путь до текущего документа со скриптом}\docs\pagination
                # Определяем количество файлов в папке для сохранения документа с ответом запроса
                # Полученное значение используем для формирования имени документа
                if not os.path.exists('./pagination'):
                    os.mkdir('./pagination')
                nextFileName = './pagination/{}.json'.format(len(os.listdir('./pagination')))
                # Создаем новый документ, записываем в него ответ запроса, после закрываем
                f = open(nextFileName, mode='w', encoding='utf8')
                f.write(json.dumps(jsObj, ensure_ascii=False))
                f.close()
                # Проверка на последнюю страницу, если вакансий меньше 2000
                if (jsObj['pages'] - page) <= 1:
                   break
                try:
                    if jsObj['request_id']:
                        os.remove(nextFileName)
                        print('Лимит исчерпан. Можете сменить IP или подождать 80 минут.')
                        time.sleep(4800)
                except:
                    pass
            except:
                pass
        print('Страницы поиска собраны', area)

def getAllVacancies():
    """
    Создаем метод для разбора страниц с вакансиями по отдельным вакансиям.
    Аргументы:
        path_src - путь папки, где лежат страницы с вакансиями
        path_dst - путь пустой папки, куда будут перемещаться разобранные страницы с вакансиями
    """
    if not os.path.exists('./pagination_done'):
        os.mkdir('./pagination')
    start_time = time.time()
    stop = 0
    for fl in os.listdir('./pagination'):
        if stop:
            break
        print(fl)
        # Открываем файл, читаем его содержимое, закрываем файл
        f = open('./pagination/{}'.format(fl), encoding='utf8')
        jsonText = f.read()
        f.close()
        # Преобразуем полученный текст в объект справочника
        jsonObj = json.loads(jsonText)
        # Получаем и проходимся по непосредственно списку вакансий
        for v in jsonObj['items']:
            # Обращаемся к API и получаем детальную информацию по конкретной вакансии
            req = requests.get(v['url'])
            data = req.content.decode()
            req.close()
            # Создаем файл в формате json с идентификатором вакансии в качестве названия
            # Записываем в него ответ запроса и закрываем файл
            if not os.path.exists('./vacancies'):
                os.mkdir('./vacancies')
            fileName = f'./vacancies/{v["id"]}.json'
            f = open(fileName, mode='w', encoding='utf8')
            f.write(data)
            f.close()
            f = open(fileName, mode='r', encoding='utf8')
            jsonText = f.read()
            f.close()
            jsonObj = json.loads(jsonText)
            try:
                if jsonObj['request_id']:
                    print('Лимит исчерпан. Можете сменить IP или подождать 80 минут.')
                    print("Итерация длилась %s мин" % ((time.time() - start_time) / 60))
                    stop = 1
                    os.remove(fileName)
                    time.sleep(4800)
            except:
                try:
                    shutil.move(f'./pagination/{fl}', f'./pagination_done/{fl}')
                except:
                    print(f'Не удалось переместить {fl}')

def makeDataframe():
    # В выводе будем отображать прогресс
    # Для этого узнаем общее количество файлов, которые надо обработать
    # Счетчик обработанных файлов установим в ноль
    cnt_docs = len(os.listdir('./vacancies'))
    i, vac = 0, []
    # Проходимся по всем файлам в папке vacancies
    for fl in os.listdir('./vacancies'):
        # Открываем, читаем и закрываем файл
        f = open('./vacancies/{}'.format(fl), encoding='utf8')
        jsonText = f.read()
        f.close()
        # Текст файла переводим в справочник
        try:
            jsonObj = json.loads(jsonText)
            vac.append(jsonObj)
        except:
            print('Ошибка')
        # Увеличиваем счетчик обработанных файлов на 1, очищаем вывод ячейки и выводим прогресс
        i += 1
        display.clear_output(wait=True)
        display.display('Готово {} из {}'.format(i, cnt_docs))
    # Возврвщаем пандосовский датафрейм, который затем сохраняем в файл в таблицу vacancies
    return pd.DataFrame(vac)



