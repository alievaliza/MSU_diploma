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

def getAllPages(df_areas, wait, from_area = 0):
    """
    Создаем метод для получения 20 * len(df_areas) страниц с вакансиями.
    Аргументы:
        df_areas - датафрейм с id регионов
        wait - время ожидания следующего запроса после исчерпания лимита
        from_area - индекс региона, с которого начинается запрос
    """
    areas = len(df_areas)
    if not os.path.exists('./pagination'):
        os.mkdir('./pagination')
    for i in tqdm(range(from_area, areas)):
        area = df_areas['id'][i]
        # Считываем первые 2000 вакансий
        for page in range(20):
            # Преобразуем текст ответа запроса в справочник Python
            try:
                jsObj = json.loads(getPage(page, area))
            except:
                print(f'\nЛимит исчерпан. Можете сменить IP и перезапустить getAllPages с from_area = {i} или подождать {int(wait/60)} минут.', e)
                time.sleep(wait)
            try:
                if jsObj['request_id']:
                    print(f'\nЛимит исчерпан. Можете сменить IP и перезапустить getAllPages с from_area = {i} или подождать {int(wait / 60)} минут.')
                    time.sleep(wait)
            except:
                pass
            # Проверка на количество вакансий в регионе = 0 или на количество страниц
            if jsObj['found'] == 0 or page + 1 > jsObj['pages']:
                break
            # Сохраняем файлы в папку {путь до текущего документа со скриптом}\pagination
            nextFileName = f'./pagination/{df_areas["id"][i]}_{page}.json'
            # Создаем новый документ, записываем в него ответ запроса, после закрываем
            f = open(nextFileName, mode='w', encoding='utf8')
            f.write(json.dumps(jsObj, ensure_ascii=False))
            f.close()

def getAllVacancies(wait):
    """
    Создаем метод для разбора страниц с вакансиями по отдельным вакансиям.
    Аргумент:
       wait - время ожидания следующего запроса после исчерпания лимита
    """
    if not os.path.exists('./pagination_done'):
        os.mkdir('./pagination_done')
    if not os.path.exists('./vacancies'):
        os.mkdir('./vacancies')
    start_time = time.time()
    for fl in tqdm(os.listdir('./pagination')):
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
                    print(f'\nЛимит исчерпан. Можете сменить IP и перезапустить getAllVacancies или подождать {int(wait/60)} минут.')
                    print("Итерация длилась %s мин" % (int((time.time() - start_time) / 60)))
                    os.remove(fileName)
                    time.sleep(wait)
            except:
                try:
                    shutil.move(f'./pagination/{fl}', f'./pagination_done/{fl}')
                except:
                    pass

def makeDataframe():
    # В выводе будем отображать прогресс
    # Для этого узнаем общее количество файлов, которые надо обработать
    # Счетчик обработанных файлов установим в ноль
    cnt_docs = len(os.listdir('./vacancies'))
    i, vac = 0, []
    # Проходимся по всем файлам в папке vacancies
    for fl in tqdm(os.listdir('./vacancies')):
        # Открываем, читаем и закрываем файл
        f = open('./vacancies/{}'.format(fl), encoding='utf8')
        jsonText = f.read()
        f.close()
        # Текст файла переводим в справочник
        try:
            jsonObj = json.loads(jsonText)
            vac.append(jsonObj)
        except:
            print(f'Ошибка в файле {fl}')
        # Увеличиваем счетчик обработанных файлов на 1, очищаем вывод ячейки и выводим прогресс
        i += 1
        display.clear_output(wait=True)
        # display.display('Готово {} из {}'.format(i, cnt_docs))
    # Возвращаем пандосовский датафрейм, который затем сохраняем в файл в таблицу vacancies
    return pd.DataFrame(vac)